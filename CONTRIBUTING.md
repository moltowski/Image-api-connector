# Contributing to API Connector

Thank you for your interest in contributing to API Connector! This document provides guidelines for contributing to the project.

## Ways to Contribute

### 1. Report Bugs 🐛
- Check if the bug has already been reported
- Use the GitHub Issues template
- Include:
  - ComfyUI version
  - Python version
  - Error messages/logs
  - Steps to reproduce
  - Expected vs actual behavior

### 2. Suggest Features 💡
- Search existing feature requests
- Describe the use case clearly
- Explain why it would benefit users
- Consider implementation complexity

### 3. Improve Documentation 📚
- Fix typos or unclear explanations
- Add examples or use cases
- Translate documentation
- Update outdated information

### 4. Submit Code Changes 🔧
- Fork the repository
- Create a feature branch
- Follow coding standards below
- Test your changes
- Submit a pull request

## Development Setup

### Prerequisites
```bash
# Clone the fork
git clone https://github.com/yourusername/ComfyUI-APIConnector.git
cd ComfyUI-APIConnector

# Install dependencies
pip install -r requirements.txt

# (Optional) Install dev dependencies
pip install black flake8 pytest
```

### Project Structure
```
ComfyUI-APIConnector/
├── api_connector.py      # Main node implementation
├── __init__.py           # Node registration
├── requirements.txt      # Runtime dependencies
├── README.md             # User documentation
├── TESTING.md            # Test guide
├── CHANGELOG.md          # Version history
├── example_workflow.json # Example workflow
└── LICENSE               # MIT license
```

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use descriptive variable names

### Code Formatting
```bash
# Format code with black
black api_connector.py __init__.py

# Check with flake8
flake8 api_connector.py __init__.py --max-line-length=120
```

### Comments
- Use docstrings for functions/classes
- Comment complex logic
- Avoid obvious comments

### Example:
```python
def tensor2pil(image_tensor):
    """
    Convert ComfyUI tensor format to PIL Image.
    
    Args:
        image_tensor: Torch tensor with shape (B=1, H, W, C)
        
    Returns:
        PIL.Image.Image: RGB image or None if invalid
    """
    if image_tensor is None or image_tensor.shape[0] == 0:
        return None
    # ... implementation
```

## Adding New Models

When adding support for a new fal.ai model:

### 1. Update the Model List
```python
"model": (["existing_models", "new_model_name"],),
```

### 2. Add Model-Specific Logic
```python
elif model == "new_model_name":
    url = "https://fal.run/fal-ai/model-endpoint"
    payload = {
        "prompt": prompt,
        "image_urls": img_data_uris,
        # ... model-specific parameters
    }
    # Add validation if needed
```

### 3. Update Documentation
- Add to model table in README.md
- Document constraints and parameters
- Add example usage
- Update CHANGELOG.md

### 4. Test Thoroughly
- Test with various inputs
- Check error handling
- Verify NSFW controls work (if applicable)
- Test edge cases

## Testing Guidelines

### Before Submitting
- [ ] Code compiles without syntax errors
- [ ] Tested with at least 2 different models
- [ ] Tested with valid and invalid inputs
- [ ] Error messages are clear and helpful
- [ ] No breaking changes to existing functionality
- [ ] Documentation updated

### Manual Testing
Follow the guide in `TESTING.md` for comprehensive testing.

### Unit Tests (Future)
```python
# Example test structure (not yet implemented)
def test_tensor2pil():
    tensor = torch.rand(1, 512, 512, 3)
    image = tensor2pil(tensor)
    assert image is not None
    assert image.size == (512, 512)
```

## Pull Request Process

### 1. Create a Fork
```bash
# Fork on GitHub, then:
git clone https://github.com/yourusername/ComfyUI-APIConnector.git
cd ComfyUI-APIConnector
git remote add upstream https://github.com/originaluser/ComfyUI-APIConnector.git
```

### 2. Create a Branch
```bash
# Use descriptive branch names
git checkout -b feature/add-model-xyz
git checkout -b fix/aspect-ratio-validation
git checkout -b docs/improve-readme
```

### 3. Make Changes
- Write clean, documented code
- Follow the coding standards above
- Test thoroughly

### 4. Commit Changes
```bash
# Use clear commit messages
git add .
git commit -m "feat: Add support for Model XYZ

- Added model endpoint and payload configuration
- Implemented model-specific validation
- Updated README with model details
- Added test case in TESTING.md"
```

### Commit Message Format
```
type: Short description (max 50 chars)

Detailed explanation if needed (max 72 chars per line)
- Bullet points for multiple changes
- Reference issue numbers: #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 5. Push and Create PR
```bash
git push origin feature/add-model-xyz
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference any related issues
- Screenshots if UI changes
- Test results

### 6. Code Review
- Respond to feedback constructively
- Make requested changes
- Push updates to the same branch
- Be patient and respectful

## Adding API Providers

To add support for non-fal.ai APIs:

### 1. Abstract the API Layer
```python
class APIProvider:
    def call_api(self, model, payload):
        pass

class FalAIProvider(APIProvider):
    # Current implementation
    
class ReplicateProvider(APIProvider):
    # New provider implementation
```

### 2. Update Node Inputs
```python
"api_provider": (["fal.ai", "replicate", "novita"],),
```

### 3. Route to Correct Provider
```python
if api_provider == "fal.ai":
    result = fal_provider.call_api(model, payload)
elif api_provider == "replicate":
    result = replicate_provider.call_api(model, payload)
```

### 4. Document New Provider
- API key requirements
- Pricing differences
- Supported models
- Configuration steps

## Documentation Guidelines

### README Updates
- Keep model table up-to-date
- Add examples for new features
- Update pricing information
- Maintain clarity and conciseness

### Code Documentation
```python
def complex_function(param1, param2):
    """
    Brief description of what the function does.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
        
    Returns:
        return_type: Description of return value
        
    Raises:
        ValueError: When invalid input is provided
    """
```

## Community Guidelines

### Be Respectful
- Treat all contributors with respect
- Provide constructive feedback
- Assume good intentions
- Help newcomers learn

### Be Professional
- Keep discussions on-topic
- Avoid inflammatory language
- Focus on technical merit
- Credit others' work

### Be Collaborative
- Share knowledge freely
- Help review others' PRs
- Suggest improvements kindly
- Celebrate successes

## Questions?

- **General questions**: GitHub Discussions
- **Bug reports**: GitHub Issues
- **Feature requests**: GitHub Issues (use "enhancement" label)
- **Security issues**: Email maintainers directly (see README)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to API Connector! 🚀
