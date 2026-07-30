from .api_connector import APIConnectorEdit, SeedreamAspectRatio
from .replicate_seedream import ReplicateSeedreamEdit

NODE_CLASS_MAPPINGS = {
    "APIConnectorEdit": APIConnectorEdit,
    # Keep the historical mapping key so existing workflows keep loading, even
    # though the class is now the generic multi-model ReplicateSeedreamEdit.
    "ReplicateSeedream45Edit": ReplicateSeedreamEdit,
    "SeedreamAspectRatio": SeedreamAspectRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APIConnectorEdit": "API Connector",
    "ReplicateSeedream45Edit": "Replicate Seedream (4.5 / 5 Pro)",
    "SeedreamAspectRatio": "Seedream Aspect Ratio",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
