import base64
import os
import time
from io import BytesIO

import numpy as np
import requests
import torch
from PIL import Image


# ---------------------------------------------------------------------------
# Per-model Replicate configuration.
#
# Two families are supported through the SAME node, dispatched on "family":
#
#   * "seedream" (ByteDance) - size / aspect_ratio / image_input / max_images /
#     disable_safety_checker, and a "custom" size with explicit width/height.
#     Output is a list of images (max_images honoured).
#
#   * "nano" (Google Nano Banana) - image_input / aspect_ratio / output_format
#     and per-model extras (resolution, safety_filter_level, google_search,
#     image_search, allow_fallback_model). Output is a SINGLE image (no
#     max_images concept on Replicate).
#
# The frontend extension web/replicate_dynamic.js mirrors the "ui" data below to
# show/hide and repopulate widgets per selected model. Keep the two in sync.
# ---------------------------------------------------------------------------

# Aspect-ratio option sets (order = dropdown order; "match_input_image" first).
_AR_SEEDREAM = ["match_input_image", "21:9", "16:9", "3:2", "4:3", "1:1", "3:4", "2:3", "9:16"]
_AR_NANO_STD = ["match_input_image", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
# Nano Banana 2 / 2 Lite add the extreme panorama/strip ratios.
_AR_NANO_EXT = _AR_NANO_STD + ["1:4", "4:1", "1:8", "8:1"]

REPLICATE_MODELS = {
    "seedream-4.5": {
        "family": "seedream",
        "endpoint": "https://api.replicate.com/v1/models/bytedance/seedream-4.5/predictions",
        "sizes": ("2K", "4K", "custom"),
        "aspect_ratios": _AR_SEEDREAM,
        "max_input_images": 14,
    },
    "seedream-5-pro": {
        "family": "seedream",
        "endpoint": "https://api.replicate.com/v1/models/bytedance/seedream-5-pro/predictions",
        "sizes": ("1K", "2K", "custom"),
        "aspect_ratios": _AR_SEEDREAM,
        "max_input_images": 10,
    },
    "nano-banana-pro": {
        "family": "nano",
        "endpoint": "https://api.replicate.com/v1/models/google/nano-banana-pro/predictions",
        "aspect_ratios": _AR_NANO_STD,
        "resolutions": ["1K", "2K", "4K"],
        "resolution_default": "2K",
        "output_formats": ["png", "jpg"],
        "safety": True,          # exposes safety_filter_level
        "fallback": True,        # exposes allow_fallback_model
        "grounding": False,
        "max_input_images": 14,
    },
    "nano-banana-2": {
        "family": "nano",
        "endpoint": "https://api.replicate.com/v1/models/google/nano-banana-2/predictions",
        "aspect_ratios": _AR_NANO_EXT,
        # Live schema enum is ["1K","2K","4K"] (the readme's "512px" is not a
        # valid API value); model's own default is "1K".
        "resolutions": ["1K", "2K", "4K"],
        "resolution_default": "2K",
        "output_formats": ["jpg", "png"],
        "safety": False,
        "fallback": False,
        "grounding": True,       # exposes google_search / image_search
        "max_input_images": 14,
    },
    "nano-banana-2-lite": {
        "family": "nano",
        "endpoint": "https://api.replicate.com/v1/models/google/nano-banana-2-lite/predictions",
        "aspect_ratios": _AR_NANO_EXT,
        "resolutions": None,     # fixed 1K, no resolution input
        "output_formats": ["jpg", "png"],
        "safety": False,
        "fallback": False,
        "grounding": False,
        "max_input_images": 14,
    },
}

# Fixed number of optional image slots exposed on the node. The per-model cap
# is enforced at call time against the images actually connected.
IMAGE_SLOTS = 14

# Superset dropdown option lists (a valid value for at least one model). The JS
# extension narrows these to the selected model; the backend also validates.
ASPECT_RATIOS = _AR_NANO_EXT  # widest set; contains every seedream value too
RESOLUTIONS = ["1K", "2K", "4K"]
SIZES = ["1K", "2K", "4K", "custom"]
OUTPUT_FORMATS = ["png", "jpg"]
SAFETY_FILTER_LEVELS = ["block_only_high", "block_medium_and_above", "block_low_and_above"]


def _tensor_item_to_pil(image_array):
    image = np.clip(255.0 * image_array, 0, 255).astype(np.uint8)
    channels = image.shape[-1]

    if channels == 1:
        image = np.repeat(image, 3, axis=-1)
    elif channels == 3:
        pass
    elif channels == 4:
        image = image[..., :3]
    else:
        raise ValueError(f"Unsupported channels: {channels}. Expected 1, 3, or 4.")

    return Image.fromarray(image, mode="RGB")


def tensor_batch_to_pils(image_tensor):
    if image_tensor is None or image_tensor.shape[0] == 0:
        return []

    image_batch = image_tensor.cpu().numpy()
    return [_tensor_item_to_pil(image_batch[index]) for index in range(image_batch.shape[0])]


def pil2tensor(pil_image):
    if pil_image is None:
        return None
    arr = np.array(pil_image.convert("RGB")).astype(np.float32) / 255.0
    arr = arr[np.newaxis, ...]
    return torch.from_numpy(arr)


def pil_to_data_uri(pil_image):
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def decode_output_image(output_item):
    if isinstance(output_item, dict):
        output_item = output_item.get("url") or output_item.get("data_uri")

    if not isinstance(output_item, str) or not output_item:
        raise ValueError(f"Unsupported Replicate output item: {output_item!r}")

    if output_item.startswith("data:"):
        _, encoded = output_item.split(",", 1)
        return Image.open(BytesIO(base64.b64decode(encoded))).convert("RGB")

    response = requests.get(output_item, timeout=120)
    if response.status_code != 200:
        raise ValueError(f"Failed to download generated image: HTTP {response.status_code}")
    return Image.open(BytesIO(response.content)).convert("RGB")


def _parse_token_line(raw):
    """Accept either a bare token or a `REPLICATE_API_TOKEN=r8_...` style line."""
    token = raw.strip()
    if not token:
        return ""
    # Take the last non-empty line (tolerates trailing newlines / comments above).
    for line in reversed(token.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[len("export "):].strip()
        if "=" in line and line.split("=", 1)[0].strip().upper() in (
            "REPLICATE_API_TOKEN",
            "REPLICATE_TOKEN",
        ):
            line = line.split("=", 1)[1].strip()
        return line.strip().strip('"').strip("'")
    return ""


def _token_file_candidates():
    override = os.environ.get("REPLICATE_TOKEN_FILE", "").strip()
    candidates = []
    if override:
        candidates.append(override)
    # Default: a local, gitignored file living next to this node on the pod, e.g.
    # /workspace/ComfyUI/custom_nodes/Image-api-connector/replicate_token.txt
    # Both a visible (.txt) and a dotfile name are accepted; whichever exists wins.
    node_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(node_dir, "replicate_token.txt"))
    candidates.append(os.path.join(node_dir, ".replicate_token"))
    return candidates


def get_replicate_token():
    """Resolve the Replicate token.

    Order: REPLICATE_API_TOKEN env var, then a local `.replicate_token` file
    (gitignored). The token is deliberately NOT a node widget: keeping it out of
    INPUT_TYPES means the secret is never shown in the ComfyUI graph and never
    serialized into a saved workflow .json. The file is read at execution time,
    so dropping it in place takes effect on the next run without restarting
    ComfyUI.
    """
    token = os.environ.get("REPLICATE_API_TOKEN", "").strip()
    if token:
        return token

    for path in _token_file_candidates():
        try:
            with open(path, "r", encoding="utf-8") as handle:
                file_token = _parse_token_line(handle.read())
        except OSError:
            continue
        if file_token:
            return file_token

    raise ValueError(
        "No Replicate token found. Set REPLICATE_API_TOKEN in the ComfyUI "
        "environment, or drop the token in a '.replicate_token' file next to "
        "this node (or point REPLICATE_TOKEN_FILE at one)."
    )


def collect_image_data_uris(image_inputs, max_input_images):
    data_uris = []
    for image_tensor in image_inputs:
        for pil_image in tensor_batch_to_pils(image_tensor):
            data_uris.append(pil_to_data_uri(pil_image))

    if len(data_uris) > max_input_images:
        raise ValueError(
            f"This model accepts at most {max_input_images} input images. "
            f"Received {len(data_uris)} images across connected inputs/batches."
        )

    return data_uris


def build_seedream_input(
    model,
    prompt,
    image_input,
    size,
    aspect_ratio,
    width,
    height,
    max_images,
    disable_safety_checker,
):
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is required.")

    allowed_sizes = REPLICATE_MODELS[model]["sizes"]
    if size not in allowed_sizes:
        raise ValueError(
            f"{model} supports size {list(allowed_sizes)} only. Got '{size}'."
        )

    if aspect_ratio == "match_input_image" and not image_input:
        raise ValueError("aspect_ratio='match_input_image' requires at least one input image.")

    payload = {
        "prompt": prompt,
        "size": size,
        "max_images": max(1, min(int(max_images), 15)),
    }

    if image_input:
        payload["image_input"] = image_input

    if size == "custom":
        if width <= 0 or height <= 0:
            raise ValueError("Custom size requires width and height.")
        if not (1024 <= width <= 4096 and 1024 <= height <= 4096):
            raise ValueError("Replicate Seedream custom width/height must be 1024-4096px.")
        payload["width"] = int(width)
        payload["height"] = int(height)
    else:
        payload["aspect_ratio"] = aspect_ratio

    if disable_safety_checker:
        payload["disable_safety_checker"] = True

    return payload


def build_nano_input(
    model,
    config,
    prompt,
    image_input,
    aspect_ratio,
    resolution,
    output_format,
    safety_filter_level,
    google_search,
    image_search,
    allow_fallback_model,
):
    """Build the Replicate input payload for a Google Nano Banana model.

    Only fields the selected model actually supports are included, so the shared
    superset of widgets never leaks an unsupported field into the request.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is required.")

    payload = {"prompt": prompt}

    if image_input:
        payload["image_input"] = image_input

    # Aspect ratio: "match_input_image" only makes sense with an input image;
    # otherwise omit and let the model choose its default.
    if aspect_ratio == "match_input_image":
        if image_input:
            payload["aspect_ratio"] = "match_input_image"
    elif aspect_ratio:
        if aspect_ratio not in config["aspect_ratios"]:
            raise ValueError(
                f"{model} does not support aspect_ratio '{aspect_ratio}'. "
                f"Allowed: {config['aspect_ratios']}"
            )
        payload["aspect_ratio"] = aspect_ratio

    # Output format (jpg/png) - always supported by nano models.
    if output_format:
        payload["output_format"] = output_format

    # Resolution - only some models expose it (lite is fixed 1K).
    resolutions = config.get("resolutions")
    if resolutions:
        if resolution not in resolutions:
            resolution = config.get("resolution_default", resolutions[0])
        payload["resolution"] = resolution

    # Safety filter level - Nano Banana Pro only.
    if config.get("safety"):
        payload["safety_filter_level"] = safety_filter_level

    # Search grounding - Nano Banana 2 only.
    if config.get("grounding"):
        if google_search:
            payload["google_search"] = True
        if image_search:
            payload["image_search"] = True

    # Capacity fallback - Nano Banana Pro only.
    if config.get("fallback") and allow_fallback_model:
        payload["allow_fallback_model"] = True

    return payload


def create_prediction(token, endpoint, input_payload, wait_seconds):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": f"wait={max(1, min(int(wait_seconds), 60))}",
    }
    response = requests.post(
        endpoint,
        json={"input": input_payload},
        headers=headers,
        timeout=max(65, int(wait_seconds) + 10),
    )
    # 200/201 = termine/cree ; 202 = accepte, encore en cours (le Prefer: wait a expire)
    # -> dans les 3 cas le corps est une prediction valide avec urls.get ; poll_prediction prend le relais.
    if response.status_code not in (200, 201, 202):
        raise ValueError(f"Replicate API error {response.status_code}: {response.text}")
    return response.json()


def poll_prediction(token, prediction, timeout_seconds, poll_interval):
    headers = {"Authorization": f"Bearer {token}"}
    deadline = time.time() + timeout_seconds

    while prediction.get("status") not in {"succeeded", "failed", "canceled"}:
        if time.time() >= deadline:
            prediction_id = prediction.get("id", "unknown")
            raise TimeoutError(f"Replicate prediction timed out: {prediction_id}")

        get_url = prediction.get("urls", {}).get("get")
        if not get_url:
            raise ValueError(f"Replicate response missing polling URL: {prediction}")

        time.sleep(max(0.5, poll_interval))
        response = requests.get(get_url, headers=headers, timeout=60)
        if response.status_code != 200:
            raise ValueError(f"Replicate poll error {response.status_code}: {response.text}")
        prediction = response.json()

    if prediction.get("status") != "succeeded":
        raise ValueError(f"Replicate prediction failed: {prediction.get('error') or prediction}")

    return prediction


class ReplicateSeedreamEdit:
    @classmethod
    def INPUT_TYPES(cls):
        optional_images = {f"image{i}": ("IMAGE",) for i in range(1, IMAGE_SLOTS + 1)}
        return {
            "required": {
                "prompt": ("STRING", {"default": "Edit or generate an image.", "multiline": True}),
                "model": (list(REPLICATE_MODELS.keys()), {"default": "seedream-5-pro"}),
                # No replicate_token widget on purpose: the token is read from the
                # REPLICATE_API_TOKEN env var so it is never shown in the graph nor
                # saved into the workflow .json.
                "aspect_ratio": (ASPECT_RATIOS, {"default": "match_input_image"}),
            },
            "optional": {
                **optional_images,
                # --- Seedream family ---
                "size": (SIZES, {"default": "2K"}),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15}),
                "disable_safety_checker": ("BOOLEAN", {"default": False, "label_on": "Relax safety checker", "label_off": "Default safety"}),
                "width": ("INT", {"default": 0, "min": 0, "max": 4096, "display": "number"}),
                "height": ("INT", {"default": 0, "min": 0, "max": 4096, "display": "number"}),
                # --- Nano Banana family ---
                "resolution": (RESOLUTIONS, {"default": "2K"}),
                "output_format": (OUTPUT_FORMATS, {"default": "png"}),
                "safety_filter_level": (SAFETY_FILTER_LEVELS, {"default": "block_only_high"}),
                "google_search": ("BOOLEAN", {"default": False, "label_on": "Web search grounding", "label_off": "No web grounding"}),
                "image_search": ("BOOLEAN", {"default": False, "label_on": "Image search grounding", "label_off": "No image grounding"}),
                "allow_fallback_model": ("BOOLEAN", {"default": False, "label_on": "Allow fallback model", "label_off": "No fallback"}),
                # --- Shared plumbing ---
                "timeout_seconds": ("INT", {"default": 300, "min": 60, "max": 1800}),
                "poll_interval": ("FLOAT", {"default": 2.0, "min": 0.5, "max": 10.0, "step": 0.5}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run_seedream"
    CATEGORY = "image/api"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        # Remote API calls should run for every queued ComfyUI generation.
        return time.time()

    def run_seedream(
        self,
        prompt,
        model,
        aspect_ratio,
        size="2K",
        max_images=1,
        disable_safety_checker=False,
        width=0,
        height=0,
        resolution="2K",
        output_format="png",
        safety_filter_level="block_only_high",
        google_search=False,
        image_search=False,
        allow_fallback_model=False,
        timeout_seconds=300,
        poll_interval=2.0,
        **kwargs,
    ):
        if model not in REPLICATE_MODELS:
            raise ValueError(f"Unknown model '{model}'. Expected one of {list(REPLICATE_MODELS)}.")

        config = REPLICATE_MODELS[model]
        token = get_replicate_token()

        image_tensors = [kwargs.get(f"image{i}") for i in range(1, IMAGE_SLOTS + 1)]
        image_input = collect_image_data_uris(image_tensors, config["max_input_images"])

        if config["family"] == "seedream":
            input_payload = build_seedream_input(
                model=model,
                prompt=prompt,
                image_input=image_input,
                size=size,
                aspect_ratio=aspect_ratio,
                width=width,
                height=height,
                max_images=max_images,
                disable_safety_checker=disable_safety_checker,
            )
            output_cap = max(1, min(int(max_images), 15))
        else:  # nano
            input_payload = build_nano_input(
                model=model,
                config=config,
                prompt=prompt,
                image_input=image_input,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_format=output_format,
                safety_filter_level=safety_filter_level,
                google_search=google_search,
                image_search=image_search,
                allow_fallback_model=allow_fallback_model,
            )
            output_cap = 1  # nano models return a single image

        prediction = create_prediction(token, config["endpoint"], input_payload, timeout_seconds)
        prediction = poll_prediction(token, prediction, timeout_seconds, poll_interval)

        output = prediction.get("output")
        if not output:
            raise ValueError(f"Replicate returned no output: {prediction}")
        if not isinstance(output, list):
            output = [output]

        tensors = []
        for output_item in output[:output_cap]:
            tensors.append(pil2tensor(decode_output_image(output_item)))

        if not tensors:
            raise ValueError("No generated images could be decoded from Replicate output.")

        return (torch.cat(tensors, dim=0),)


# Backwards-compatible alias: existing workflows reference the old class name.
ReplicateSeedream45Edit = ReplicateSeedreamEdit
