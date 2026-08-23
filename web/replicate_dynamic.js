import { app } from "../../scripts/app.js";

// Dynamic widget visibility for the "Replicate Seedream / Nano Banana" node.
// Shows only the widgets the selected model actually accepts, and narrows the
// aspect_ratio / resolution / size dropdowns to that model's allowed values.
// Mirrors REPLICATE_MODELS in replicate_seedream.py - keep the two in sync.

const NODE_NAME = "ReplicateSeedream45Edit";

const AR_SEEDREAM = ["match_input_image", "21:9", "16:9", "3:2", "4:3", "1:1", "3:4", "2:3", "9:16"];
const AR_NANO_STD = ["match_input_image", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"];
const AR_NANO_EXT = AR_NANO_STD.concat(["1:4", "4:1", "1:8", "8:1"]);

// Per-model spec: which optional widgets to show, and the option sets for the
// shared dropdowns. `resolutions: null` means the model has no resolution input.
const MODELS = {
    "seedream-4.5": {
        show: ["size", "max_images", "disable_safety_checker", "width", "height"],
        aspect_ratios: AR_SEEDREAM,
        sizes: ["2K", "4K", "custom"],
        resolutions: null,
    },
    "seedream-5-pro": {
        show: ["size", "max_images", "disable_safety_checker", "width", "height"],
        aspect_ratios: AR_SEEDREAM,
        sizes: ["1K", "2K", "custom"],
        resolutions: null,
    },
    "nano-banana-pro": {
        show: ["resolution", "output_format", "safety_filter_level", "allow_fallback_model"],
        aspect_ratios: AR_NANO_STD,
        sizes: null,
        resolutions: ["1K", "2K", "4K"],
    },
    "nano-banana-2": {
        show: ["resolution", "output_format", "google_search", "image_search"],
        aspect_ratios: AR_NANO_EXT,
        sizes: null,
        resolutions: ["1K", "2K", "4K"],
    },
    "nano-banana-2-lite": {
        show: ["output_format"],
        aspect_ratios: AR_NANO_EXT,
        sizes: null,
        resolutions: null,
    },
};

// All optional widgets this node can toggle (union across models).
const TOGGLEABLE = [
    "size", "max_images", "disable_safety_checker", "width", "height",
    "resolution", "output_format", "safety_filter_level",
    "google_search", "image_search", "allow_fallback_model",
];

const HIDDEN_TYPE = "replicate_hidden";

function findWidget(node, name) {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
}

function hideWidget(node, widget) {
    if (!widget || widget.type === HIDDEN_TYPE) return;
    widget._origType = widget.type;
    widget._origComputeSize = widget.computeSize;
    widget.type = HIDDEN_TYPE;
    widget.computeSize = () => [0, -4]; // collapse the row (accounts for row gap)
}

function showWidget(node, widget) {
    if (!widget || widget._origType === undefined) return;
    widget.type = widget._origType;
    widget.computeSize = widget._origComputeSize;
    widget._origType = undefined;
    widget._origComputeSize = undefined;
}

// Replace a combo widget's option list and clamp its value into the new set.
function setComboOptions(widget, values) {
    if (!widget || !values) return;
    widget.options = widget.options || {};
    widget.options.values = values;
    if (!values.includes(widget.value)) {
        const fallback = values.includes("2K") ? "2K" : values[0];
        widget.value = fallback;
        if (widget.callback) widget.callback(widget.value);
    }
}

function applyModel(node) {
    const modelWidget = findWidget(node, "model");
    if (!modelWidget) return;
    const spec = MODELS[modelWidget.value];
    if (!spec) return;

    // Narrow the shared dropdowns to this model's allowed values.
    setComboOptions(findWidget(node, "aspect_ratio"), spec.aspect_ratios);
    if (spec.sizes) setComboOptions(findWidget(node, "size"), spec.sizes);
    if (spec.resolutions) setComboOptions(findWidget(node, "resolution"), spec.resolutions);

    // Decide the visible set. width/height only matter for seedream "custom".
    const show = new Set(spec.show);
    if (show.has("width") || show.has("height")) {
        const sizeWidget = findWidget(node, "size");
        const isCustom = sizeWidget && sizeWidget.value === "custom";
        if (!isCustom) {
            show.delete("width");
            show.delete("height");
        }
    }

    for (const name of TOGGLEABLE) {
        const w = findWidget(node, name);
        if (!w) continue;
        if (show.has(name)) showWidget(node, w);
        else hideWidget(node, w);
    }

    const sz = node.computeSize();
    // Never shrink below the manually-set width; only fix the height.
    node.setSize([Math.max(node.size[0], sz[0]), sz[1]]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "moltowski.replicate.dynamic",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_NAME) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;

            const modelWidget = findWidget(node, "model");
            if (modelWidget) {
                const origCb = modelWidget.callback;
                modelWidget.callback = function () {
                    const ret = origCb ? origCb.apply(this, arguments) : undefined;
                    applyModel(node);
                    return ret;
                };
            }
            // Re-evaluate width/height when the seedream size changes.
            const sizeWidget = findWidget(node, "size");
            if (sizeWidget) {
                const origCb = sizeWidget.callback;
                sizeWidget.callback = function () {
                    const ret = origCb ? origCb.apply(this, arguments) : undefined;
                    applyModel(node);
                    return ret;
                };
            }

            // Defer once so widgets restored from a saved graph are in place.
            setTimeout(() => applyModel(node), 0);
            return r;
        };

        // Also runs when a node is loaded from a saved workflow.
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const r = onConfigure ? onConfigure.apply(this, arguments) : undefined;
            const node = this;
            setTimeout(() => applyModel(node), 0);
            return r;
        };
    },
});
