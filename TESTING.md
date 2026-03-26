# Test Guide for API Connector Node

This document provides guidance for testing the API Connector node after installation.

## Prerequisites

1. ComfyUI installed and running
2. API Connector node installed in `custom_nodes/`
3. Valid fal.ai API key
4. Test images prepared

## Test Cases

### Test 1: Basic Seedream 5 Lite Test

**Objective**: Verify Seedream 5 Lite integration works

**Setup**:
- Model: `seedream_5_lite`
- Images: 1 test image (any portrait or landscape)
- Prompt: "Enhance with professional lighting"
- Resolution: 2K (or leave width/height at 0)
- NSFW: Safe Mode (unchecked)
- Num Images: 1
- Seed: 42

**Expected Result**: 
- Single edited image returned
- Processing time: 20-40 seconds
- No errors

**Success Criteria**: ✅ Image generated successfully

---

### Test 2: NSFW Toggle Test

**Objective**: Verify NSFW checkbox controls safety checker

**Setup A (Safe Mode)**:
- Model: `seedream_5_lite`
- Images: 1 test image
- Prompt: "Add romantic sunset atmosphere"
- NSFW: **Unchecked** (Safe Mode)

**Expected Result A**: 
- Image processed normally
- Safety checker enabled in API call

**Setup B (Allow NSFW)**:
- Same as above, but NSFW: **Checked** (Allow NSFW)

**Expected Result B**: 
- Image processed normally
- Safety checker disabled in API call
- Potentially less filtered results

**Success Criteria**: ✅ Both modes work without errors

---

### Test 3: Multi-Image Input Test

**Objective**: Verify multi-image support for Seedream 5 Lite

**Setup**:
- Model: `seedream_5_lite`
- Images: 5 different test images
- Prompt: "Combine elements from all images"
- Resolution: 2K
- Num Images: 2

**Expected Result**: 
- 2 variations generated
- Images show influence from multiple inputs
- Processing time: 40-60 seconds

**Success Criteria**: ✅ Multiple images processed and combined

---

### Test 4: Aspect Ratio Validation Test

**Objective**: Verify aspect ratio constraints for Seedream 5 Lite

**Setup A (Valid Aspect Ratio)**:
- Model: `seedream_5_lite`
- Images: 1 test image
- Width: 2048
- Height: 512 (aspect = 4:1, valid)

**Expected Result A**: ✅ Processes successfully

**Setup B (Invalid Aspect Ratio)**:
- Width: 2048
- Height: 100 (aspect = 20.48:1, invalid)

**Expected Result B**: 
❌ Error: "Seedream 5 Lite: Aspect ratio must be between 1:16 and 16:1"

**Success Criteria**: ✅ Validation works correctly

---

### Test 5: Compare Seedream 4.5 vs 5 Lite

**Objective**: Compare output quality between versions

**Setup for Both**:
- Same test image
- Same prompt: "Professional portrait enhancement"
- Same seed: 12345
- Resolution: 2048x2048 (both support)

**Model A**: `seedream_4.5`
**Model B**: `seedream_5_lite`

**Expected Differences**:
- Version 5 may have better text rendering
- Version 5 may show more contextual understanding
- Both should produce high-quality results

**Success Criteria**: ✅ Both generate images, note quality differences

---

### Test 6: Nano Banana Quick Test

**Objective**: Verify Nano models still work correctly

**Setup**:
- Model: `nano_banana`
- Images: 1 test image
- Prompt: "Add vibrant colors"
- Aspect Ratio: 16:9
- Resolution: 1K
- NSFW: Any (ignored by this model)

**Expected Result**: 
- Fast processing (10-20 seconds)
- Lower cost than Seedream
- Width/height settings ignored

**Success Criteria**: ✅ Image generated using aspect ratio

---

### Test 7: Flux 2 Edit Test

**Objective**: Verify Flux models work with size constraints

**Setup**:
- Model: `flux_2_edit`
- Images: 1 test image
- Prompt: "Artistic enhancement"
- Width: 1024
- Height: 1024
- NSFW: Safe Mode

**Expected Result**: 
- High-quality edit
- Size validated (512-2048px range)
- Longer processing time

**Success Criteria**: ✅ Image generated within constraints

---

### Test 8: Batch Generation Test

**Objective**: Verify multiple outputs work correctly

**Setup**:
- Model: `seedream_5_lite`
- Images: 1 test image
- Prompt: "Creative variation"
- Num Images: 4
- Different seeds for variety

**Expected Result**: 
- 4 different variations returned
- All images in single batch tensor
- Cost = 4x single image

**Success Criteria**: ✅ Batch tensor contains 4 images

---

### Test 9: Error Handling Test

**Objective**: Verify proper error messages

**Test A - No API Key**:
- fal_key: "your_fal_key_here" (default)
- Expected: ❌ "Please set your fal.ai API key in the node."

**Test B - No Images**:
- No images connected
- Expected: ❌ "At least one image input must be connected."

**Test C - Invalid Size (Flux 2)**:
- Model: flux_2_edit
- Width: 4096 (too large)
- Expected: ❌ "Flux 2 Edit: Size must be 512-2048px."

**Success Criteria**: ✅ Clear error messages displayed

---

### Test 10: Seed Reproducibility Test

**Objective**: Verify same seed produces same results

**Setup**:
- Model: `seedream_5_lite`
- Images: 1 test image
- Prompt: "Test consistency"
- Seed: 999
- Run twice

**Expected Result**: 
- Both runs produce identical (or very similar) images
- Demonstrates reproducibility

**Success Criteria**: ✅ Results are reproducible

---

## Testing Checklist

- [ ] All 8 models load in dropdown
- [ ] NSFW checkbox appears and works
- [ ] API key field accepts input
- [ ] Single image input works
- [ ] Multiple image inputs work (2-5)
- [ ] Custom width/height work
- [ ] Aspect ratio presets work
- [ ] Resolution presets work
- [ ] Seed values work
- [ ] Num_images generates batches
- [ ] Seedream 5 Lite validates aspect ratio
- [ ] Error messages are clear
- [ ] Output images display in ComfyUI
- [ ] Images can be saved/exported
- [ ] Node works in larger workflows

## Common Issues

**"Module not found: requests"**
→ Run: `pip install requests`

**"API error: 401 Unauthorized"**
→ Check your API key is correct and active

**"API error: 402 Payment Required"**
→ Add credits to your fal.ai account

**"Connection timeout"**
→ Check internet connection, try again

**Images are low quality**
→ Increase resolution or try different model

**Safety checker blocking content**
→ Enable "Allow NSFW" if appropriate

## Performance Benchmarks

Approximate processing times (varies by system/network):

| Model | 1K Resolution | 2K Resolution | 4K Resolution |
|-------|--------------|--------------|--------------|
| Nano Banana | 10-15s | 15-20s | 20-30s |
| Seedream 5 Lite | 25-35s | 35-45s | N/A |
| Flux 2 Edit | 30-40s | 40-60s | N/A |

## Notes

- All tests require active internet connection
- API costs apply for each test
- Use low-cost models (Nano) for initial testing
- Test with small images first
- Keep test images under 5MB for faster uploads

## Reporting Issues

If you encounter bugs:

1. Note the exact error message
2. Record your settings (model, resolution, etc.)
3. Check the console for detailed errors
4. Report to GitHub Issues with:
   - ComfyUI version
   - Python version
   - Error message
   - Steps to reproduce

---

**Happy Testing!** 🚀
