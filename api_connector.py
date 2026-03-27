import torch 
import requests 
import base64 
import numpy as np 
from io import BytesIO 
from PIL import Image 
 
# Helper function to convert ComfyUI tensor (B=1, H, W, C) to PIL Image (RGB) 
def tensor2pil(image_tensor): 
    if image_tensor is None or image_tensor.shape[0] == 0: 
        return None 
    i = 255. * image_tensor[0].cpu().numpy() 
    image = np.clip(i, 0, 255).astype(np.uint8) 
    
    c = image.shape[-1] 
    if c == 1: 
        image = np.repeat(image, 3, axis=-1) 
    elif c == 3: 
        pass 
    elif c == 4: 
        image = image[..., :3] 
    else: 
        raise ValueError(f"Unsupported channels: {c}. Expected 1, 3, or 4.") 
    
    return Image.fromarray(image, mode='RGB') 
 
# Helper function to convert PIL Image (RGB) back to ComfyUI tensor (B=1, H, W, C) 
def pil2tensor(pil_image): 
    if pil_image is None: 
        return None 
    arr = np.array(pil_image).astype(np.float32) / 255.0 
    arr = arr[np.newaxis, ...] 
    return torch.from_numpy(arr) 
 
# Main node class 
class APIConnectorEdit: 
    @classmethod 
    def INPUT_TYPES(cls): 
        return { 
            "required": { 
                "prompt": ("STRING", {"default": "Edit the image according to this prompt.", "multiline": True}), 
                "model": (["nano_banana", "nano_banana_pro", "seedream_4.5", "seedream_5_lite", "qwen_edit_plus", "flux_2_edit", "flux_2_pro", "flux_2_flex"],), 
                "fal_key": ("STRING", {"default": "your_fal_key_here"}), 
            }, 
            "optional": { 
                "image1": ("IMAGE",), 
                "image2": ("IMAGE",), 
                "image3": ("IMAGE",), 
                "image4": ("IMAGE",), 
                "image5": ("IMAGE",), 
                "width": ("INT", {"default": 0, "min": 0, "max": 4096, "display": "number"}), 
                "height": ("INT", {"default": 0, "min": 0, "max": 4096, "display": "number"}), 
                "num_images": ("INT", {"default": 1, "min": 1, "max": 6}), 
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}), 
                "aspect_ratio": (["auto", "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"], {"default": "auto"}), 
                "resolution": (["1K", "2K", "4K"], {"default": "1K"}), 
                "enable_nsfw": ("BOOLEAN", {"default": False, "label_on": "Allow NSFW", "label_off": "Safe Mode"}),
            } 
        } 
    
    RETURN_TYPES = ("IMAGE",) 
    RETURN_NAMES = ("edited_image",) 
    FUNCTION = "edit_image" 
    CATEGORY = "image/api" 
    OUTPUT_NODE = True 
    
    def edit_image(self, prompt, model, fal_key, image1=None, image2=None, image3=None, image4=None, image5=None, 
                   width=0, height=0, num_images=1, seed=0, aspect_ratio="auto", resolution="1K", 
                   enable_nsfw=False, acceleration="none"): 
        if fal_key == "your_fal_key_here": 
            raise ValueError("Please set your fal.ai API key in the node.") 
        
        # Collect all non-None images 
        images = [img for img in [image1, image2, image3, image4, image5] if img is not None] 
        if not images: 
            raise ValueError("At least one image input must be connected.") 
        
        # Convert each to PIL and encode 
        img_data_uris = [] 
        custom_size = (width > 0 and height > 0) 
        
        for img_tensor in images: 
            pil_image = tensor2pil(img_tensor) 
            if pil_image is None: 
                continue 
            
            if custom_size: 
                if model in ["nano_banana", "nano_banana_pro"]: 
                    pass 
                else: 
                    pil_image = pil_image.resize((width, height), Image.LANCZOS) 
            
            buffer = BytesIO() 
            pil_image.save(buffer, format="PNG") 
            img_str = base64.b64encode(buffer.getvalue()).decode() 
            img_data_uris.append(f"data:image/png;base64,{img_str}") 
        
        # Enforce limits 
        if model == "seedream_4.5" and len(img_data_uris) + num_images > 15: 
            raise ValueError("Seedream 4.5: Total inputs + outputs must <=15.") 
        
        # Convert enable_nsfw to safety_checker (inverse logic)
        enable_safety_checker = not enable_nsfw
        
        # Model-specific payloads 
        if model == "nano_banana": 
            url = "https://fal.run/fal-ai/nano-banana/edit" 
            payload = { 
                "prompt": prompt, 
                "image_urls": img_data_uris, 
                "num_images": min(num_images, 4), 
                "aspect_ratio": aspect_ratio, 
                "output_format": "png", 
                "sync_mode": True, 
            } 
        elif model == "nano_banana_pro": 
            url = "https://fal.run/fal-ai/nano-banana-pro/edit" 
            payload = { 
                "prompt": prompt, 
                "image_urls": img_data_uris, 
                "num_images": min(num_images, 4), 
                "aspect_ratio": aspect_ratio, 
                "resolution": resolution, 
                "output_format": "png", 
                "sync_mode": True, 
            } 
        elif model == "seedream_4.5":
            url = "https://fal.run/fal-ai/bytedance/seedream/v4.5/edit"
            payload = {
                "prompt": prompt,
                "image_urls": img_data_uris,
                "num_images": min(num_images, 6),
                "seed": seed,
                "enable_safety_checker": enable_safety_checker,
                "sync_mode": True,
            }
            if custom_size:
                if not (1920 <= width <= 4096 and 1920 <= height <= 4096):
                    raise ValueError("Seedream 4.5: Width/height must be 1920-4096px.")
                area = width * height
                if not (3686400 <= area <= 16777216):
                    raise ValueError(f"Seedream 4.5: Image area must be 3,686,400-16,777,216px² (min 1920×1920, max 4096×4096). Got {area}.")
                payload["image_size"] = {"width": width, "height": height}
            else:
                # Map aspect_ratio dropdown to API preset strings.
                # Valid presets: square_hd, square, portrait_4_3, portrait_16_9,
                #                landscape_4_3, landscape_16_9, auto_2K, auto_4K
                if aspect_ratio == "16:9":
                    payload["image_size"] = "landscape_16_9"
                elif aspect_ratio == "9:16":
                    payload["image_size"] = "portrait_16_9"
                elif aspect_ratio == "4:3":
                    payload["image_size"] = "landscape_4_3"
                elif aspect_ratio == "3:4":
                    payload["image_size"] = "portrait_4_3"
                elif aspect_ratio == "1:1":
                    payload["image_size"] = "square_hd"
                else:
                    # Fall back to resolution-based auto preset.
                    # Seedream 4.5 uses auto_4K (not auto_3K — that belongs to v5 Lite).
                    payload["image_size"] = "auto_4K" if resolution == "4K" else "auto_2K"
        elif model == "seedream_5_lite":
            url = "https://fal.run/fal-ai/bytedance/seedream/v5/lite/edit"
            payload = {
                "prompt": prompt,
                "image_urls": img_data_uris,
                "num_images": min(num_images, 6),
                "seed": seed,
                "enable_safety_checker": enable_safety_checker,
                "sync_mode": True,
            }
            if custom_size:
                # Aspect ratio must be between 1:16 and 16:1
                aspect = width / height
                if not (1/16 <= aspect <= 16):
                    raise ValueError(f"Seedream 5 Lite: Aspect ratio must be between 1:16 and 16:1. Got {aspect:.2f}")
                # Max output is 3072×3072 (9,437,184 px²); min is ~2560×1440 (3,686,400 px²)
                area = width * height
                if area > 9437184:
                    raise ValueError(f"Seedream 5 Lite: Image area exceeds maximum 9,437,184px² (3072×3072). Got {area}.")
                if area < 3686400:
                    raise ValueError(f"Seedream 5 Lite: Image area below minimum 3,686,400px² (approx 2560×1440). Got {area}.")
                payload["image_size"] = {"width": width, "height": height}
            else:
                # Map aspect_ratio dropdown to API preset strings.
                # Valid presets: square_hd, square, portrait_4_3, portrait_16_9,
                #                landscape_4_3, landscape_16_9, auto_2K, auto_3K
                if aspect_ratio == "16:9":
                    payload["image_size"] = "landscape_16_9"
                elif aspect_ratio == "9:16":
                    payload["image_size"] = "portrait_16_9"
                elif aspect_ratio == "4:3":
                    payload["image_size"] = "landscape_4_3"
                elif aspect_ratio == "3:4":
                    payload["image_size"] = "portrait_4_3"
                elif aspect_ratio == "1:1":
                    payload["image_size"] = "square_hd"
                else:
                    # Fall back to resolution-based auto preset.
                    # Seedream 5 Lite uses auto_3K (not auto_4K — that belongs to v4.5).
                    payload["image_size"] = "auto_3K" if resolution == "4K" else "auto_2K"
        elif model == "qwen_edit_plus": 
            url = "https://fal.run/fal-ai/qwen-image-edit-plus" 
            payload = { 
                "prompt": prompt, 
                "image_urls": img_data_uris, 
                "num_images": min(num_images, 4), 
                "seed": seed, 
                "guidance_scale": 4.0, 
                "num_inference_steps": 50, 
                "enable_safety_checker": enable_safety_checker, 
                "output_format": "png", 
                "sync_mode": True, 
                "acceleration": acceleration, 
            } 
            if custom_size: 
                payload["image_size"] = {"width": width, "height": height} 
        
        # Combined logic for Flux 2 Edit, Pro, and Flex 
        elif model in ["flux_2_edit", "flux_2_pro", "flux_2_flex"]: 
            if model == "flux_2_edit": 
                url = "https://fal.run/fal-ai/flux-2/edit" 
            elif model == "flux_2_pro": 
                url = "https://fal.run/fal-ai/flux-2-pro/edit" 
            elif model == "flux_2_flex": 
                url = "https://fal.run/fal-ai/flux-2-flex/edit" 
            
            payload = { 
                "prompt": prompt, 
                "image_urls": img_data_uris, 
                "num_images": min(num_images, 4), 
                "seed": seed, 
                "guidance_scale": 2.5, 
                "num_inference_steps": 28, 
                "enable_prompt_expansion": False, 
                "enable_safety_checker": enable_safety_checker, 
                "output_format": "png", 
                "sync_mode": True, 
                "acceleration": acceleration, 
            } 
            
            if custom_size: 
                if model == "flux_2_edit": 
                    if not (512 <= width <= 2048 and 512 <= height <= 2048): 
                        raise ValueError("Flux 2 Edit: Size must be 512-2048px.") 
                
                payload["image_size"] = {"width": width, "height": height} 
        
        # API call 
        headers = { 
            "Authorization": f"Key {fal_key}", 
            "Content-Type": "application/json", 
        } 
        response = requests.post(url, json=payload, headers=headers) 
        if response.status_code != 200: 
            raise ValueError(f"API error: {response.text}") 
        
        api_result = response.json() 
        if "images" not in api_result or len(api_result["images"]) == 0: 
            raise ValueError("No images returned from API") 
        
        all_edited_tensors = [] 
        
        # Process up to num_images 
        for img_info in api_result["images"][:num_images]: 
            img_data = img_info.get("data_uri") or img_info.get("url") 
            if not img_data: 
                continue 
            
            if img_data.startswith("data:"): 
                _, encoded = img_data.split(",", 1) 
                pil_edited = Image.open(BytesIO(base64.b64decode(encoded))) 
            else: 
                img_resp = requests.get(img_data) 
                if img_resp.status_code != 200: 
                    raise ValueError("Failed to download generated image") 
                pil_edited = Image.open(BytesIO(img_resp.content)) 
            
            tensor_edited = pil2tensor(pil_edited) 
            if tensor_edited is not None: 
                all_edited_tensors.append(tensor_edited) 
        
        # Stack output 
        if all_edited_tensors: 
            batched_output = torch.cat(all_edited_tensors, dim=0) 
        else: 
            batched_output = torch.zeros((1, 512, 512, 3)) 
        
        return (batched_output,)


# Supported Seedream aspect ratios as (label_string, float_value) pairs.
# The float is W/H so closest-match arithmetic works on a single number line.
_SEEDREAM_RATIOS = [
    ("1:1",  1 / 1),
    ("4:3",  4 / 3),
    ("3:4",  3 / 4),
    ("16:9", 16 / 9),
    ("9:16", 9 / 16),
    ("3:2",  3 / 2),
    ("2:3",  2 / 3),
    ("4:5",  4 / 5),
    ("5:4",  5 / 4),
    ("21:9", 21 / 9),
]


class SeedreamAspectRatio:
    """Computes the Seedream-supported aspect ratio that best matches an input image."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = (["auto", "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"],)
    RETURN_NAMES = ("ratio",)
    FUNCTION = "get_ratio"
    CATEGORY = "image/api"

    def get_ratio(self, image):
        # image tensor shape: (B, H, W, C)
        _, h, w, _ = image.shape
        img_ratio = w / h

        closest_label = min(_SEEDREAM_RATIOS, key=lambda r: abs(r[1] - img_ratio))[0]
        return (closest_label,)
