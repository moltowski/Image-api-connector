# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-01

### Added
- **Seedream 5 Lite support** - Latest ByteDance model with web search integration
- **Visual NSFW control** - Checkbox toggle for content filtering (Safe Mode/Allow NSFW)
- **Enhanced validation** - Aspect ratio validation (1:16 to 16:1) for Seedream 5 Lite
- **Comprehensive documentation** - README with model comparison, examples, and troubleshooting
- **Testing guide** - TESTING.md with 10 test cases and checklist
- **Example workflow** - Pre-configured ComfyUI workflow JSON

### Changed
- Renamed from NanoSeedEdit to APIConnectorEdit
- Updated display name to "API Connector"
- Changed category from "image/edit" to "image/api"
- Refactored safety checker logic (enable_nsfw → enable_safety_checker)

### Technical Details
- Forked from [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed)
- Added Seedream 5 Lite endpoint: `fal-ai/bytedance/seedream/v5/lite/edit`
- Implemented aspect ratio validation for Seedream 5 Lite
- Added NSFW parameter to INPUT_TYPES as BOOLEAN
- Updated all model payloads to support enable_safety_checker

## [Original] - ComfyUI-NanoSeed

### Original Features (Inherited)
- Nano Banana support
- Nano Banana Pro support
- Seedream 4.5 support
- Qwen Edit Plus support
- Flux 2 Edit support
- Flux 2 Pro support
- Flux 2 Flex support
- Multi-image input (up to 5 images)
- Custom resolution controls
- Aspect ratio presets
- Seed-based reproducibility
- Batch generation (up to 6 images)

### Credits
- Original author: [comrender](https://github.com/comrender)
- Original repo: [ComfyUI-NanoSeed](https://github.com/comrender/ComfyUI-NanoSeed)

---

## Future Plans

### Potential v1.1.0 Features
- [ ] Seedream 5 Standard (text-to-image)
- [ ] Separate NSFW Checker node
- [ ] Async mode with progress bar
- [ ] Result caching

### Potential v1.2.0 Features
- [ ] Prompt presets library
- [ ] Extended image inputs (10-14 for Seedream 5 Lite)
- [ ] Other API provider support (Replicate, Novita)

### Potential v2.0.0 Features
- [ ] UI redesign with tabs
- [ ] Model-specific advanced settings
- [ ] Workflow templates
- [ ] Integration with other ComfyUI nodes

---

## Contributing

If you'd like to contribute to future versions:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description
4. Update CHANGELOG.md with your changes

---

**Note**: This is the first public release of the API Connector fork. Please report any issues on GitHub!
