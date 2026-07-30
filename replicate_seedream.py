import base64
import os
import time
from io import BytesIO

import numpy as np
import requests
import torch
from PIL import Image


# Per-model Replicate configuration. Seedream 4.5 and 5 Pro share the same
# input field names (size / aspect_ratio / image_input / max_images /
# disable_safety_checker) and only differ on the endpoint, the allowed size
# presets, and the reference-image cap.
REPLICATE_MODELS = {
    "seedream-4.5": {
        "endpoint": "https://api.replicate.com/v1/models/bytedance/seedream-4.5/predictions",
        "sizes": ("2K", "4K", "custom"),
        "max_input_images": 14,
    },
    "seedream-5-pro": {
        "endpoint": "https://api.replicate.com/v1/models/bytedance/seedream-5-pro/predictions",
        "sizes": ("1K", "2K", "custom"),
        "max_input_images": 10,
    },
}

# Fixed number of optional image slots exposed on the node. The per-model cap
# above is enforced at call time against the images actually connected.
IMAGE_SLOTS = 14

ASPECT_RATIOS = ["match_input_image", "21:9", "16:9", "3:2", "4:3", "1:1", "3:4", "2:3", "9:16"]


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


def get_replicate_token():
    """Read the Replicate token from the environment only.

    The token is deliberately NOT a node widget: keeping it out of INPUT_TYPES
    means the secret is never shown in the ComfyUI graph and never serialized
    into a saved workflow .json.
    """
    token = os.environ.get("REPLICATE_API_TOKEN", "").strip()
    if not token:
        raise ValueError(
            "REPLICATE_API_TOKEN is not set. Define it in the ComfyUI process "
            "environment (e.g. export REPLICATE_API_TOKEN=r8_...)."
        )
    return token


def collect_image_data_uris(image_inputs, max_input_images):
    data_uris = []
    for image_tensor in image_inputs:
        for pil_image in tensor_batch_to_pils(image_tensor):
            data_uris.append(pil_to_data_uri(pil_image))

    if len(data_uris) > max_input_images:
        raise ValueError(
            f"This Seedream model accepts at most {max_input_images} input images. "
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
    if response.status_code not in (200, 201):
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
                "prompt": ("STRING", {"default": "Edit or generate an image with Seedream.", "multiline": True}),
                "model": (list(REPLICATE_MODELS.keys()), {"default": "seedream-5-pro"}),
                # No replicate_token widget on purpose: the token is read from the
                # REPLICATE_API_TOKEN env var so it is never shown in the graph nor
                # saved into the workflow .json.
                "size": (["1K", "2K", "4K", "custom"], {"default": "2K"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "match_input_image"}),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15}),
                "disable_safety_checker": ("BOOLEAN", {"default": False, "label_on": "Relax safety checker", "label_off": "Default safety"}),
            },
            "optional": {
                **optional_images,
                "width": ("INT", {"default": 0, "min": 0, "max": 4096, "display": "number"}),
                "height": ("INT", {"default": 0, "min": 0, "max": 4096, "display": "number"}),
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
        size,
        aspect_ratio,
        max_images,
        disable_safety_checker,
        width=0,
        height=0,
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

        prediction = create_prediction(token, config["endpoint"], input_payload, timeout_seconds)
        prediction = poll_prediction(token, prediction, timeout_seconds, poll_interval)

        output = prediction.get("output")
        if not output:
            raise ValueError(f"Replicate returned no output: {prediction}")
        if not isinstance(output, list):
            output = [output]

        tensors = []
        for output_item in output[:max_images]:
            tensors.append(pil2tensor(decode_output_image(output_item)))

        if not tensors:
            raise ValueError("No generated images could be decoded from Replicate output.")

        return (torch.cat(tensors, dim=0),)


# Backwards-compatible alias: existing workflows reference the old class name.
ReplicateSeedream45Edit = ReplicateSeedreamEdit
