import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
import { debug, _name, _endpoint, loadCSS } from "./utils.js";

loadCSS("css/aspect_ratios.css");

const extension = {
    name: _name("AspectRatiosShort"), 

    beforeRegisterNodeDef: function(nodeType, nodeData, app) {
        if (nodeType.comfyClass === _name("Aspect_Ratios_Short")) {

            const __onAdded = nodeType.prototype.onAdded;
            nodeType.prototype.onAdded = async function() {
                const r = __onAdded?.apply(this, arguments);

                this.short = this.widgets[0];
                this.step = this.widgets[1]
                this.aspectW = this.widgets[2];
                this.aspectH = this.widgets[3];
                this.preset = this.widgets[4];

                // アスペクト入れ替えボタン
                this.switchButton = this.addWidget("button", "switch ⇅", null, null)

                // 計算結果表示スペース
                const result = $el("div.jupo-aspect-ratios-result");
                const widthRow = $el("div.jupo-aspect-ratios-row");
                const heightRow = $el("div.jupo-aspect-ratios-row");

                // ラベルと値を別々の要素に
                const widthLabel = $el("span.jupo-aspect-ratios-label", { textContent: "width:"});
                const heightLabel = $el("span.jupo-aspect-ratios-label", { textContent: "height:"});
                this.resultWidthValue = $el("span.jupo-aspect-ratios-value");
                this.resultHeightValue = $el("span.jupo-aspect-ratios-value");

                // 行に追加
                widthRow.appendChild(widthLabel);
                widthRow.appendChild(this.resultWidthValue);
                heightRow.appendChild(heightLabel);
                heightRow.appendChild(this.resultHeightValue)
                
                result.appendChild(widthRow);
                result.appendChild(heightRow);
                const resultWidget = this.addDOMWidget("result", "DOM", result);
                resultWidget.computeSize = () => [, 82];

                // callback設定
                this.short.callback = () => this.updateResult();
                this.step.callback = () => this.updateResult();
                this.aspectW.callback = () => this.updateResult();
                this.aspectH.callback = () => this.updateResult();
                this.switchButton.callback = () => {
                    const temp = this.aspectW.value;
                    this.aspectW.value = this.aspectH.value;
                    this.aspectH.value = temp;
                    this.updateResult();
                };
                this.preset.callback = async (preset) => {
                    const res = await api.fetchApi(_endpoint("aspect_ratios/preset"), {
                        method: "POST", 
                        body: JSON.stringify({preset: preset})
                    });
                    const ratios = await res.json();
                    
                    const w = ratios.aspectW;
                    const h = ratios.aspectH;
                    if ((w !== null) && (h !== null)) {
                        this.aspectW.value = ratios.aspectW;
                        this.aspectH.value = ratios.aspectH;
                        this.updateResult();
                    }
                };

                this.updateResult();
                
                return r;
            };


            // 計算結果表示メソッド
            nodeType.prototype.updateResult = async function() {
                const res = await api.fetchApi(_endpoint("aspect_ratios_short/calc"), {
                    method: "POST", 
                    body: JSON.stringify({
                        short: this.short.value, 
                        step: this.step.value, 
                        aspectW: this.aspectW.value, 
                        aspectH: this.aspectH.value
                    })
                });
                const resolution = await res.json();
                const width = resolution.width;
                const height = resolution.height;

                this.resultWidthValue.textContent = width;
                this.resultHeightValue.textContent = height;

                this.setDirtyCanvas(true, false);
            };
        }
    }, 

    loadedGraphNode: function(node) {
        if (node.comfyClass === _name("Aspect_Ratios_Short")) {
            node.updateResult();
        }
    }, 
};

app.registerExtension(extension);