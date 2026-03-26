"""
Quick verification script for API Connector node.
Run this to check if the node can be imported correctly.
"""

import sys
import os

print("=" * 60)
print("API Connector - Quick Verification")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")
if sys.version_info < (3, 8):
    print("   [!] WARNING: Python 3.8+ recommended")
else:
    print("   [OK] Python version OK")

# Check dependencies
print("\n2. Checking Dependencies...")
dependencies = {
    "torch": "PyTorch (ComfyUI requirement)",
    "PIL": "Pillow (Image processing)",
    "numpy": "NumPy (Array operations)",
    "requests": "Requests (API calls)"
}

missing = []
for module, description in dependencies.items():
    try:
        __import__(module)
        print(f"   [OK] {module:12} - {description}")
    except ImportError:
        print(f"   [X] {module:12} - {description} (MISSING)")
        missing.append(module)

if missing:
    print(f"\n   [!] Missing dependencies: {', '.join(missing)}")
    print("   Install with: pip install " + " ".join(missing))
else:
    print("\n   [OK] All dependencies installed")

# Check if files exist
print("\n3. Checking Files...")
required_files = [
    "api_connector.py",
    "__init__.py",
    "requirements.txt",
    "README.md"
]

all_present = True
for filename in required_files:
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"   [OK] {filename:20} ({size:,} bytes)")
    else:
        print(f"   [X] {filename:20} (MISSING)")
        all_present = False

if not all_present:
    print("\n   [!] Some files are missing!")
else:
    print("\n   [OK] All required files present")

# Try to import the node
print("\n4. Importing Node...")
try:
    from api_connector import APIConnectorEdit
    print("   [OK] APIConnectorEdit imported successfully")
    
    # Check node structure
    print("\n5. Checking Node Structure...")
    
    if hasattr(APIConnectorEdit, 'INPUT_TYPES'):
        print("   [OK] INPUT_TYPES defined")
        
        # Get input types
        input_types = APIConnectorEdit.INPUT_TYPES()
        required = input_types.get('required', {})
        optional = input_types.get('optional', {})
        
        print(f"      - Required inputs: {len(required)}")
        print(f"      - Optional inputs: {len(optional)}")
        
        # Check for new features
        if 'enable_nsfw' in optional:
            print("   [OK] NSFW control implemented")
        else:
            print("   [!] NSFW control not found")
            
        # Check models
        models = required.get('model', [None])[0]
        if models and 'seedream_5_lite' in models:
            print(f"   [OK] Seedream 5 Lite found in {len(models)} models")
        else:
            print("   [!] Seedream 5 Lite not found")
    else:
        print("   [X] INPUT_TYPES not defined")
    
    if hasattr(APIConnectorEdit, 'RETURN_TYPES'):
        print("   [OK] RETURN_TYPES defined")
    
    if hasattr(APIConnectorEdit, 'FUNCTION'):
        print(f"   [OK] FUNCTION defined: {APIConnectorEdit.FUNCTION}")
    
    if hasattr(APIConnectorEdit, 'CATEGORY'):
        print(f"   [OK] CATEGORY defined: {APIConnectorEdit.CATEGORY}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] VERIFICATION COMPLETE - Node is ready!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Copy this folder to ComfyUI/custom_nodes/")
    print("2. Restart ComfyUI")
    print("3. Look for 'API Connector' node in the 'image/api' category")
    print("4. Get your fal.ai API key from https://fal.ai")
    print("5. See TESTING.md for test cases")
    
except ImportError as e:
    print(f"   [X] Failed to import: {e}")
    print("\n" + "=" * 60)
    print("[FAILED] VERIFICATION FAILED")
    print("=" * 60)
    print("\nTroubleshooting:")
    print("1. Make sure you're in the correct directory")
    print("2. Check that api_connector.py has no syntax errors")
    print("3. Ensure all dependencies are installed")
    
except Exception as e:
    print(f"   [X] Unexpected error: {e}")
    print("\n" + "=" * 60)
    print("[FAILED] VERIFICATION FAILED")
    print("=" * 60)

print()
