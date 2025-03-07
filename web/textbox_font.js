import { app } from "../../scripts/app.js";
import { debug, _name } from "./utils.js";

const fontSetting = {
    name: "font-family", 
    id: _name("font-family"), 
    type: "string", 
    defaultValue: "", 
    onChange: (value) => {
        // フォント変更
        if (!value) value = "sans-serif";
        updateFontFamily(value);
    }
};


// フォントを適用する関数
function updateFontFamily(font) {
    if (font) {
        // .comfy-multiline-input要素にスタイルを適用
        const styleElement = document.createElement("style");
        styleElement.textContent = `
            .comfy-multiline-input {
                font-family: "${font}", sans-serif !important;
            }
        `;
        // 既存のスタイルがあれば削除して新しいものを追加
        const existingStyle = document.getElementById("jupo-textbox-font");
        if (existingStyle) {
            existingStyle.remove();
        }
        styleElement.id = "jupo-textbox-font";
        document.head.appendChild(styleElement);
    }
}


const extension = {
    name: _name("TextBoxFont"), 

    settings: [
        fontSetting, 
    ], 

    setup: async function(app) {

        const settings = app.extensionManager.setting;
        const font = settings.get(fontSetting.id);
        updateFontFamily(font);
    }

};

app.registerExtension(extension);