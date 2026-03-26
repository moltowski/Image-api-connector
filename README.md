# ComfyUI API Connector

A ComfyUI custom node for AI-powered image editing via [fal.ai](https://fal.ai)'s API. A single unified node gives you access to 8 state-of-the-art models — from fast/cheap nano models to professional-grade Flux and ByteDance Seedream 5 Lite — without any local GPU work.

**Forked from [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed) by comrender.**
Added: Seedream 5 Lite support, visual NSFW control, extended validation, and full documentation.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-orange)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

---

## What this node does

The **API Connector** node accepts 1–5 images and a text prompt, sends them to a fal.ai image-editing endpoint of your choice, and returns the edited image(s) back into your ComfyUI graph as a standard batched `IMAGE` tensor.

All inference runs remotely on fal.ai infrastructure — no local VRAM required. You pay per image generated.

---

## Installation

### Option A — ComfyUI Manager (recommended)

1. Open **ComfyUI Manager → Install Custom Nodes**
2. Search for **API Connector**
3. Click **Install**, then restart ComfyUI

### Option B — Manual (git clone)

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/moltowski/Image-api-connector.git ComfyUI-APIConnector
cd ComfyUI-APIConnector
pip install -r requirements.txt
```

Restart ComfyUI. The node appears under **image/api → API Connector**.

### Dependencies

| Package | Source |
|---------|--------|
| `requests` | installed via `requirements.txt` |
| `torch`, `numpy`, `Pillow` | already present in any ComfyUI environment |

Python ≥ 3.8 required.

---

## Getting a fal.ai API key

1. Sign up at [fal.ai](https://fal.ai)
2. Go to **Account → API Keys → Create Key**
3. Copy the UUID-format key: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

Paste it directly into the `fal_key` field on the node, or set the environment variable `FAL_KEY` and read it in your workflow.

> **Security note:** The `fal_key` field is visible in the ComfyUI interface and saved in workflow JSON. For shared or production setups, load the key from an environment variable rather than hardcoding it in the node.

---

## Supported models

| Model ID | Provider | Max outputs | Resolution control | NSFW toggle | ~Cost/image |
|----------|----------|:-----------:|-------------------|:-----------:|------------:|
| `nano_banana` | Nano Banana | 4 | `aspect_ratio` + `resolution` preset | ✗ | ~$0.02 |
| `nano_banana_pro` | Nano Banana | 4 | `aspect_ratio` + `resolution` preset | ✗ | ~$0.03 |
| `seedream_4.5` | ByteDance | 6 | 1920–4096 px (custom) | ✓ | ~$0.035 |
| `seedream_5_lite` ⭐ | ByteDance | 6 | Named preset or custom (1:16–16:1) | ✓ | ~$0.035 |
| `qwen_edit_plus` | Alibaba | 4 | Custom `width`/`height` | ✓ | ~$0.04 |
| `flux_2_edit` | BFL | 4 | 512–2048 px (custom) | ✓ | ~$0.05 |
| `flux_2_pro` | BFL | 4 | Custom `width`/`height` | ✓ | ~$0.08 |
| `flux_2_flex` | BFL | 4 | Custom `width`/`height` | ✓ | ~$0.06 |

Pricing is approximate and subject to change on fal.ai's end. Generating `num_images = N` multiplies cost by N.

---

## Model-specific constraints

### Nano Banana / Nano Banana Pro

- `width` and `height` parameters are **ignored** — resolution is set by the `aspect_ratio` and `resolution` dropdowns.
- Nano Banana Pro additionally accepts the `resolution` field (1K/2K/4K).
- Maximum **4** output images.
- No safety-checker control in the API.

### Seedream 4.5

- Custom dimensions: both `width` and `height` must be **1920–4096 px**.
- Image area must be between **3,686,400 px²** and **16,777,216 px²** (roughly 1.92K×1.92K to 4K×4K).
- Hard limit: **(input images) + (num_images) ≤ 15**. Connecting 5 inputs caps output at 10.
- Maximum **6** output images.

### Seedream 5 Lite ⭐

ByteDance's newest editing model (2026). Notable extras over 4.5:

- **Web search integration** — can incorporate real-world context into edits
- **Multi-step reasoning** — better handling of complex spatial instructions
- **Enhanced multilingual text rendering**
- API supports up to 14 input images (this node's UI is limited to 5)

Resolution behaviour:

| Condition | What gets sent |
|-----------|---------------|
| `width` + `height` both > 0 | `image_size: {width, height}` — aspect ratio must be 1:16–16:1 |
| `aspect_ratio = 16:9` | `"landscape_16_9"` |
| `aspect_ratio = 9:16` | `"portrait_16_9"` |
| `aspect_ratio = 4:3` | `"landscape_4_3"` |
| `aspect_ratio = 3:4` | `"portrait_4_3"` |
| `aspect_ratio = 1:1` | `"square_hd"` |
| any other / `resolution = 2K or 1K` | `"auto_2K"` |
| `resolution = 4K` | `"auto_3K"` |

Maximum **6** output images.

### Qwen Edit Plus

- Custom `width`/`height` accepted freely.
- Fixed internal settings: `guidance_scale = 4.0`, `num_inference_steps = 50`.
- Maximum **4** output images.

### Flux 2 Edit

- **Strict resolution check**: both `width` and `height` must be **512–2048 px**. The node raises an error before calling the API if this is violated.
- Fixed internal settings: `guidance_scale = 2.5`, `num_inference_steps = 28`.
- Maximum **4** output images.

### Flux 2 Pro / Flux 2 Flex

- Same internal settings as Flux 2 Edit but without the 512–2048 px hard limit.
- Accept custom `width`/`height` freely.
- Maximum **4** output images.

---

## Input parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | STRING (multiline) | Natural-language instruction for the edit |
| `model` | DROPDOWN | Which model endpoint to call |
| `fal_key` | STRING | Your fal.ai API key |

### Optional — images

| Parameter | Type | Description |
|-----------|------|-------------|
| `image1` … `image5` | IMAGE | Reference images. At least one must be connected. Passed as base64 PNG data URIs. |

### Optional — generation settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | INT 0–4096 | 0 | Output width in pixels. `0` = use preset/auto. |
| `height` | INT 0–4096 | 0 | Output height in pixels. `0` = use preset/auto. |
| `num_images` | INT 1–6 | 1 | Number of variations to generate. Each costs independently. |
| `seed` | INT 0–4294967295 | 0 | Fixed seed for reproducible results. |
| `aspect_ratio` | DROPDOWN | `auto` | Preset ratio — used by Nano models and as a fallback for Seedream 5 Lite. Options: `auto`, `21:9`, `16:9`, `3:2`, `4:3`, `5:4`, `1:1`, `4:5`, `3:4`, `2:3`, `9:16` |
| `resolution` | DROPDOWN | `1K` | Rough output scale — `1K`, `2K`, `4K`. Used by Nano Banana Pro and as a fallback for Seedream 5 Lite. |
| `enable_nsfw` | BOOLEAN | `False` (Safe Mode) | `False` = safety checker **on**; `True` = safety checker **off**. Applies to Seedream 4.5, Seedream 5 Lite, Qwen, and all Flux 2 models. |

### Output

| Name | Type | Description |
|------|------|-------------|
| `edited_image` | IMAGE | Batched tensor `(N, H, W, 3)` where N = number of images returned. Compatible with all standard ComfyUI image nodes (Preview, Save, VAE Encode, etc.). |

---

## Usage

### Minimal workflow

```
[Load Image] → image1 → [API Connector] → edited_image → [Preview Image]
```

1. Search **API Connector** in the node browser (category: `image/api`)
2. Connect at least one image to `image1`
3. Paste your fal.ai key into `fal_key`
4. Write a prompt
5. Queue the workflow

### Example configurations

#### Quick test — Nano Banana (cheapest)
```
model:        nano_banana
prompt:       "Add dramatic sunset lighting"
image1:       <your image>
aspect_ratio: 4:3
resolution:   1K
num_images:   1
```

#### High-quality portrait edit — Seedream 5 Lite
```
model:       seedream_5_lite
prompt:      "Enhance with professional studio lighting, sharp details"
image1:      <your portrait>
resolution:  2K
seed:        42
num_images:  2
enable_nsfw: False (Safe Mode)
```

#### Style transfer batch — Flux 2 Pro
```
model:      flux_2_pro
prompt:     "Transform into impressionist oil painting"
image1:     <your image>
width:      1024
height:     1024
num_images: 4
seed:       12345
```

#### Multi-image scene composition — Seedream 5 Lite
```
model:        seedream_5_lite
prompt:       "Combine elements from all images into a single cohesive scene"
image1–image5: <your 5 images>
aspect_ratio: 16:9
num_images:   2
seed:         0
```

---

## Troubleshooting

### `"Please set your fal.ai API key in the node."`
The `fal_key` field still contains the default placeholder. Replace it with your actual key.

### `"At least one image input must be connected."`
No `imageN` socket has an active connection. Connect at least one image node.

### `"Seedream 4.5: Total inputs + outputs must <=15."`
Reduce `num_images` or disconnect some input images so that `inputs + outputs ≤ 15`.

### `"Seedream 4.5: Width/height must be 1920–4096px."`
Set both `width` and `height` to values in the 1920–4096 range, or set them to `0` to let the API choose automatically.

### `"Seedream 5 Lite: Aspect ratio must be between 1:16 and 16:1."`
Your custom `width`/`height` values produce an extreme ratio. Bring them closer to square, or set both to `0` to use a named preset.

### `"Flux 2 Edit: Size must be 512–2048px."`
Both `width` and `height` must be in the 512–2048 range for this model. Use `flux_2_pro` or `flux_2_flex` for unconstrained sizes.

### `"No images returned from API"`
- Verify your API key is valid and your fal.ai account has credits.
- Check whether the safety checker blocked the prompt (`enable_nsfw` is `False` by default). Try rephrasing the prompt.
- Some prompts time out on the API side — retry with a simpler prompt first.

### `"API error: …"`
The raw fal.ai error is included. Common causes:
- Invalid/expired API key → regenerate at fal.ai
- Insufficient credits → top up at fal.ai
- Malformed payload (usually a resolution constraint) → check the model-specific constraints above

### Slow responses / timeouts
Generation is synchronous (`sync_mode: true`). Large sizes or high `num_images` can take 30–90 seconds. If ComfyUI times out, try:
- Reducing `num_images`
- Lowering resolution
- Using a faster model (Nano Banana)

---

## Performance tips

- **Start cheap** — use `nano_banana` at `1K` for prompt iteration. Switch to a premium model once the prompt is solid.
- **Use seeds** — set a non-zero `seed` to reproduce a result exactly before scaling up resolution or `num_images`.
- **Batch efficiently** — `num_images = 4` costs 4× but avoids 4 round-trips. Use it when you want variations; use `num_images = 1` when iterating.
- **Resize inputs** — inputs are resized to `width × height` before encoding (except Nano models). Sending huge images through ComfyUI doesn't increase quality, only upload time.

---

## Roadmap

- [ ] Seedream 5 Standard (text-to-image)
- [ ] Expand UI to 14 input sockets for Seedream 5 Lite
- [ ] Async mode with progress updates
- [ ] Support for other providers (Replicate, Novita, etc.)
- [ ] Result caching to reduce redundant API calls
- [ ] Prompt presets / template library

---

## Credits

**Original project**: [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed) by [comrender](https://github.com/comrender) — MIT License

**This fork adds**: Seedream 5 Lite support, visual NSFW checkbox, enhanced input validation, and this documentation.

**Powered by**: [fal.ai](https://fal.ai) inference infrastructure

---

## License

MIT — see [LICENSE](LICENSE).

---

## Support

- **Bug reports / feature requests**: [GitHub Issues](https://github.com/moltowski/Image-api-connector/issues)
- **fal.ai questions**: [fal.ai Discord](https://discord.gg/fal-ai)

---

## Disclaimer

This node requires a fal.ai account and charges usage fees. You are responsible for:

- Your API usage costs
- Compliance with fal.ai's [Terms of Service](https://fal.ai/terms)
- Lawful and responsible use of the `enable_nsfw` toggle
- Respecting copyright in source images and generated outputs

The authors are not liable for API costs, generated content, or misuse.
