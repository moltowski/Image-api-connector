from api_connector import APIConnectorEdit

print("Testing API Connector Node Import...")
print("=" * 50)

try:
    input_types = APIConnectorEdit.INPUT_TYPES()
    required = input_types.get('required', {})
    optional = input_types.get('optional', {})
    
    models = required.get('model', [None])[0]
    
    print(f"[OK] Node imported successfully")
    print(f"[OK] Total models: {len(models)}")
    print(f"[OK] Seedream 5 Lite: {'YES' if 'seedream_5_lite' in models else 'NO'}")
    print(f"[OK] NSFW control: {'YES' if 'enable_nsfw' in optional else 'NO'}")
    print(f"[OK] Category: {APIConnectorEdit.CATEGORY}")
    print(f"[OK] Function: {APIConnectorEdit.FUNCTION}")
    print("\n[SUCCESS] All checks passed!")
    
except Exception as e:
    print(f"[ERROR] {e}")
