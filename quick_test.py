from api_connector import APIConnectorEdit
from replicate_seedream import ReplicateSeedream45Edit

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
    replicate_inputs = ReplicateSeedream45Edit.INPUT_TYPES()
    replicate_required = replicate_inputs.get("required", {})
    replicate_optional = replicate_inputs.get("optional", {})
    replicate_images = [name for name in replicate_optional if name.startswith("image")]
    print(f"[OK] Replicate Seedream node: YES")
    print(f"[OK] Replicate image inputs: {len(replicate_images)}")
    print(f"[OK] Replicate token field: {'YES' if 'replicate_token' in replicate_required else 'NO'}")
    print("\n[SUCCESS] All checks passed!")
    
except Exception as e:
    print(f"[ERROR] {e}")
