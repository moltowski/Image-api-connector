# API Connector - Quick Start Guide

## What is this?

API Connector is a ComfyUI custom node that lets you edit images using AI models from fal.ai. This is a fork of ComfyUI-NanoSeed with added features:

- **Seedream 5 Lite** - Latest ByteDance model with web search capabilities
- **NSFW Control** - Visual checkbox to enable/disable content filtering
- **8 Models Total** - From fast Nano Banana to powerful Flux 2 Pro

## Installation (5 Minutes)

### Step 1: Copy to ComfyUI

Copy the entire `ComfyUI-APIConnector` folder to your ComfyUI custom nodes directory:

```
ComfyUI/
└── custom_nodes/
    └── ComfyUI-APIConnector/    ← Copy here
```

**Windows Example:**
```
C:\Users\YourName\ComfyUI\custom_nodes\ComfyUI-APIConnector\
```

### Step 2: Restart ComfyUI

Close and reopen ComfyUI completely.

### Step 3: Find the Node

In ComfyUI, right-click → Add Node → image → api → **API Connector**

### Step 4: Get API Key

1. Visit https://fal.ai
2. Sign up / Login
3. Go to Settings → API Keys
4. Create new key
5. Copy the key (looks like: `12345678-1234-1234-1234-123456789abc`)

### Step 5: First Test

1. Add "Load Image" node → Connect to API Connector
2. Add "Preview Image" node → Connect from API Connector
3. In API Connector:
   - Model: `nano_banana` (cheapest for testing)
   - fal_key: Paste your API key
   - Prompt: "Add vibrant colors"
   - Enable NSFW: Leave unchecked (Safe Mode)
4. Run workflow!

## Basic Workflow

```
[Load Image] → [API Connector] → [Preview/Save Image]
```

## Models Quick Reference

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| nano_banana | ⚡⚡⚡ | $ | Quick edits, testing |
| nano_banana_pro | ⚡⚡ | $$ | Better quality Nano |
| seedream_4.5 | ⚡ | $$ | High resolution |
| seedream_5_lite ⭐ | ⚡ | $$ | Latest, web search |
| qwen_edit_plus | ⚡ | $$$ | Instruction-based |
| flux_2_edit | ⚡ | $$$ | High fidelity |
| flux_2_pro | 🐌 | $$$$ | Professional grade |

⭐ = New in this fork

## NSFW Control

**Checkbox in node interface:**
- ☐ Unchecked = Safe Mode (default) - Filters mature content
- ☑ Checked = Allow NSFW - Disables filtering

Works with: Seedream, Qwen, Flux models (not Nano Banana)

## Common Settings

### For Quick Edits (Fast & Cheap)
```
Model: nano_banana
Resolution: 1K
Aspect Ratio: 16:9
Num Images: 1
```

### For High Quality (Slower & More Expensive)
```
Model: seedream_5_lite
Width: 2048
Height: 2048
Num Images: 2
Seed: 42 (for reproducibility)
```

### For Multiple Variations
```
Model: flux_2_edit
Num Images: 4
Seed: Different each time
```

## Troubleshooting

### "Please set your fal.ai API key"
→ You need to paste your API key from fal.ai into the `fal_key` field

### "At least one image input must be connected"
→ Connect a "Load Image" node to image1 socket

### "API error: 401 Unauthorized"
→ Your API key is invalid or expired

### "API error: 402 Payment Required"
→ Add credits to your fal.ai account at https://fal.ai/billing

### Node doesn't appear in ComfyUI
→ Make sure folder is in `custom_nodes/` and restart ComfyUI

### "Seedream 5 Lite: Aspect ratio must be between 1:16 and 16:1"
→ Your width/height ratio is too extreme. Try 2048x2048 or 2048x1024

## Cost Estimates

**Per Image:**
- Nano Banana: ~$0.02
- Seedream 5 Lite: $0.035
- Flux 2 Pro: ~$0.08

**Batch of 4 images = 4x the cost**

Example: 4 images with Flux 2 Pro = ~$0.32

## Tips

1. **Test with Nano first** - Cheapest way to test prompts
2. **Use seeds** - Same seed = same result
3. **Start low resolution** - Test at 1K before going 4K
4. **Check your balance** - Monitor fal.ai credits
5. **Read the docs** - See README.md for advanced features

## Example Prompts

### Enhancement
- "Professional studio lighting"
- "Enhance colors and contrast"
- "Add cinematic depth of field"

### Style Transfer
- "Transform into oil painting style"
- "Make it look like a vintage photograph"
- "Convert to anime art style"

### Creative Edits
- "Add dramatic sunset in the background"
- "Change season to winter with snow"
- "Add neon cyberpunk lighting"

## File Structure

```
ComfyUI-APIConnector/
├── api_connector.py      # Main code
├── __init__.py           # Registration
├── requirements.txt      # Dependencies
├── README.md             # Full documentation
├── TESTING.md            # Test guide
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # How to contribute
├── quick_test.py         # Import test
└── example_workflow.json # Example workflow
```

## Getting Help

- **Full Documentation**: Read `README.md`
- **Testing Guide**: Read `TESTING.md`
- **Report Issues**: GitHub Issues
- **fal.ai Help**: https://discord.gg/fal-ai

## Next Steps

1. ✅ Test with Nano Banana model
2. ✅ Try different prompts
3. ✅ Experiment with Seedream 5 Lite
4. ✅ Read README.md for advanced features
5. ✅ Check TESTING.md for comprehensive tests

## Credits

**Original**: [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed) by comrender

**This Fork**: Added Seedream 5 Lite, NSFW controls, enhanced documentation

**Powered By**: [fal.ai](https://fal.ai) API

---

**Need help?** Check README.md for detailed documentation!
