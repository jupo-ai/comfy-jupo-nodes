import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
import { _name, _endpoint } from "./utils.js";

const extension = {
    name: _name("JoinStrings"), 

    beforeRegisterNodeDef: function(nodeType, nodeData, app) {
        if (nodeType.comfyClass === _name("Join_Strings")) {

            const __onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function(side, slot, connected, link_info) {
                const r = __onConnectionsChange?.apply(this, arguments);

                // 入力のとき(side === 1)
                if (side === 1) {
                    this.adjustInputs();
                }

                return r;
            };

            nodeType.prototype.adjustInputs = function() {
                // this.inputsを走査して、一番上以外の未接続のスロットを削除
                const inputsToRemove = [];

                // 入力スロットをチェック(インデックス0は保持)
                for (let i = 1; i < this.inputs.length; i++) {
                    if (!this.inputs[i].link) { // 未接続の場合
                        inputsToRemove.push(i);
                    }
                }

                // 削除対象のスロットを後ろから順に削除(インデックスがずれないように)
                for (let i = inputsToRemove.length - 1; i >= 0; i--) {
                    this.removeInput(inputsToRemove[i]);
                }

                // 必要に応じて新しい入力スロットを追加
                if (this.inputs.length > 0 && this.inputs[this.inputs.length - 1].link) {
                    this.addInput(`text_${this.inputs.length}`, "STRING");
                    this.inputs[this.inputs.length - 1].label = "text";
                }
            };
        }
    }, 
};

app.registerExtension(extension);