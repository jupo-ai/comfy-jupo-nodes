import comfy.model_base
import comfy.model_sampling
import comfy.utils
import folder_paths
import comfy
from comfy.model_patcher import ModelPatcher
from comfy.sd import CLIP, VAE, save_checkpoint

import torch
from pathlib import Path
from .fields import Field
from .utils import log, category


def get_savepath(name: str):
    checkpoints_dir = folder_paths.get_folder_paths("checkpoints")[0]

    if not Path(name).suffix == ".safetensors":
        name += ".safetensors"

    save_path = Path(checkpoints_dir, name)

    # 連番処理
    i = 1
    temp_path = save_path
    while temp_path.exists():
        temp_path = temp_path.with_stem(f"{save_path.stem}_{i}")
        i += 1
    
    save_path = temp_path
    return save_path


def create_metadata(model: ModelPatcher, save_path: Path):
        metadata = {}

        enable_modelspec = True
        arch_key = "modelspec.architecture"
        if isinstance(model.model, comfy.model_base.SDXL):
            if isinstance(model.model, comfy.model_base.SDXL_instructpix2pix):
                metadata[arch_key] = "stable-diffusion-xl-v1-edit"
            else:
                metadata[arch_key] = "stable-diffusion-xl-v1-base"
        
        elif isinstance(model.model, comfy.model_base.SDXLRefiner):
            metadata[arch_key] = "stable-diffusion-xl-v1-refiner"
        
        elif isinstance(model.model, comfy.model_base.SVD_img2vid):
            metadata[arch_key] = "stable-video-diffusion-img2vid-v1"
        
        elif isinstance(model.model, comfy.model_base.SD3):
            metadata[arch_key] = "stable-diffusion-v3-mediumu"
        
        else:
            enable_modelspec = False
        
        if enable_modelspec:
            metadata["modelspec.sai_model_spec"] = "1.0.0"
            metadata["modelcpec.implementation"] = "sgm"
            metadata["modelspec.title"] = save_path.stem
        

        if model.model.model_type == comfy.model_base.ModelType.EPS:
            metadata["modelspec.predict_key"] = "epsilon"
        
        elif model.model.model_type == comfy.model_base.ModelType.V_PREDICTION:
            metadata["modelspec.predict_key"] = "v"
        
        return metadata


DTYPE_MAPPING = {
    "fp16": torch.float16, 
    "bf16": torch.bfloat16, 
    "fp32": torch.float32, 
    "fp8": torch.float8_e4m3fn, 
}


class SaveCheckpoint:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": Field.model(), 
                "clip": Field.clip(), 
                "vae": Field.vae(), 
                "name": Field.string(default="model")
            }
        }
    
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, model: ModelPatcher, clip: CLIP, vae: VAE, name: str):
        save_path = get_savepath(name)
        metadata = create_metadata(model, save_path)

        extra_keys = {}
        model_sampling = model.get_model_object("model_sampling")
        if isinstance(model_sampling, comfy.model_sampling.ModelSamplingContinuousEDM):
            if isinstance(model_sampling, comfy.model_sampling.V_PREDICTION):
                extra_keys["edm_vpred.sigma_max"] = torch.tensor(model_sampling.sigma_max).float()
                extra_keys["edm_vpred.sigma_min"] = torch.tensor(model_sampling.sigma_min).float()
    
        # save
        log(f"Saving ... {save_path}")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_checkpoint(
            output_path=save_path, 
            model=model, 
            clip=clip, 
            vae=vae, 
            metadata=metadata, 
            extra_keys=extra_keys
        )
        log("Save completed!")
        return ()


