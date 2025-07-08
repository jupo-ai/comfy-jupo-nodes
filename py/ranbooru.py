from comfy.comfy_types import IO
from .fields import Field
from .utils import category, endpoint

import datetime
import requests
import random
from typing import Literal
import os
import torch
import numpy as np
from PIL import Image
import io
import re

POST_AMOUNT = 100


def pil_to_tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)



class Danbooru:
    def __init__(self):
        self.base_url = "https://danbooru.donmai.us/posts.json"
        self.headers = {"User-Agent": "my-app/0.0.1"}
        self.post_amount = POST_AMOUNT

    def get_data(self, tags="", max_pages=1):
        page = random.randint(1, max_pages)
        params = {
            "limit": self.post_amount, 
            "page": page, 
            "tags": tags
        }
        res = requests.get(self.base_url, headers=self.headers, params=params)
        res.raise_for_status()
        return res.json()



RATING_TYPES = {
    "All": "All",
    "Safe": "g",
    "Sensitive": "s",
    "Questionable": "q",
    "Explicit": "e",
}


# ===============================================
# Ranbooru
# ===============================================
class Ranbooru:
    def __init__(self):
        self.artist_tags = []
        self.copyright_tags = []
        self.character_tags = []
        self.general_tags = []

        self.file_url = ""
        self.image = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "max_pages": Field.int(default=1, min=1, max=100), 
                "search": Field.string(), 
                "exclude": Field.string(), 
                "artist": Field.boolean(default=False), 
                "copyright": Field.boolean(default=False), 
                "character": Field.boolean(default=False), 
                "rating": Field.combo(choices=list(RATING_TYPES.keys())), 
                "seed": Field.int(default=0), 
            }
        }
        
    RETURN_TYPES = (IO.STRING, IO.IMAGE)
    CATEGORY = category
    FUNCTION = "execute"
    
    
    def execute(self, max_pages: int, search: str, exclude: str, artist: bool, copyright: bool, character: bool, rating: str, seed: int):
        
        # 最終結果から取り除くタグ
        bad_tags = {
            "mixed-language_text",
            "watermark",
            "text",
            "english_text",
            "speech_bubble",
            "signature",
            "artist_name",
            "censored",
            "bar_censor",
            "translation",
            "twitter_username",
            "twitter_logo",
            "patreon_username",
            "commentary_request",
            "tagme",
            "commentary",
            "character_name",
            "mosaic_censoring",
            "instagram_username",
            "text_focus",
            "english_commentary",
            "comic",
            "translation_request",
            "fake_text",
            "translated",
            "paid_reward_available",
            "thought_bubble",
            "silent_comic",
            "out-of-frame_censoring",
            "symbol-only_commentary",
            "3koma",
            "2koma",
            "character_watermark",
            "japanese_text",
            "spanish_text",
            "language_text",
            "fanbox_username",
            "commission",
            "original",
            "ai_generated",
            "stable_diffusion",
            "tagme_(artist)",
            "text_bubble",
            "qr_code",
            "chinese_commentary",
            "korean_text",
            "partial_commentary",
            "chinese_text",
            "copyright_request",
            "censored_nipples",
            "page_number",
            "scan",
            "fake_magazine_cover",
            "korean_commentary", 
            "x_logo", 
        }
        
        # そもそも検索から除外するタグ
        ban_tags = {
            "animated", "video", "multiple_views", 
            "yaoi", "gay", "bl", "male_focus", "2boys", 
            "gore", "blood", "violence", "guro", 
            "ryona", "torture", 
            "scat", "vomit", "fart", 
        }
        
        api = Danbooru()
        img_url = None
        if seed >= 0:
            random.seed(seed)
        else:
            random.seed(None)

        search_tags = search.split(",") # ','で区切る
        search_tags = [tag.strip().replace(" ", "_") for tag in search_tags if tag.strip()] # 各タグの前後の空白を削除し、間の空白は'_'に変換
        
        exclude_tags = exclude.split(",")
        exclude_tags = [f"-{tag}".strip().replace(" ", "_") for tag in exclude_tags if tag.strip()] # 同上の処理に加えて'-'を各タグに付与
        
        add_tags = search_tags + exclude_tags
        
        if rating != "All":
            add_tags.append(f"rating:{RATING_TYPES.get(rating)}")

        data = api.get_data(" ".join(add_tags), max_pages)
        if not data:
            data = [{}]
        
        count = 0
        while count <= 100:
            # 取得したデータからランダムに1つポストを決定
            random_post = random.choice(data)
            
            # タグを取得
            self.artist_tags = random_post.get("tag_string_artist", "").split()
            self.copyright_tags = random_post.get("tag_string_copyright", "").split()
            self.character_tags = random_post.get("tag_string_character", "").split()
            meta_tags = random_post.get("tag_string_meta", "").split()
            self.general_tags = random_post.get("tag_string_general", "").split()
            self.general_tags = random.sample(self.general_tags, k=len(self.general_tags)) # 一般タグのみランダムに並び替える
            
            temp_tags = []
            if artist:
                temp_tags += self.artist_tags
            if copyright:
                temp_tags += self.copyright_tags
            if character:
                temp_tags += self.character_tags
            temp_tags += self.general_tags
            
            # ban_tagsがないなら終了
            if not any(tag in ban_tags for tag in temp_tags+meta_tags):
                break
            
            count += 1
            print("ban tag が見つかりました")
            random.seed(seed + count)
                

        # タグ整形
        clean_tags = [tag for tag in temp_tags if tag not in bad_tags]
        clean_tags = [tag.replace("(", "\\(").replace(")", "\\)") for tag in clean_tags]
        clean_tags = [tag.replace("_", " ") for tag in clean_tags]
        final_tags = ", ".join(clean_tags)

        # 画像を取得
        variants = random_post.get("media_asset", {}).get("variants", [])
        img_url = None

        # 720画像を探す
        for v in variants:
            if v.get("type") == "720x720":
                img_url = v.get("url")
                break
        
        # 見つからなければ file_url にフォールバック
        if not img_url:
            img_url = random_post.get("file_url")
        
        try:
            res = requests.get(img_url)
            img = Image.open(io.BytesIO(res.content))
        except:
            img = Image.new("RGB", (512, 512), color="black")
        # rgb
        if img.mode != "RGB":
            img = img.convert("RGB")
        self.file_url = img_url
        self.image = img
        
        print(f"POST: https://danbooru.donmai.us/posts/{random_post.get("id", "")}")
        print(f"IMAGE: {self.file_url}")

        return (final_tags, pil_to_tensor(img))

            