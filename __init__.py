from .api_connector import APIConnectorEdit, SeedreamAspectRatio
from .replicate_seedream import ReplicateSeedream45Edit

NODE_CLASS_MAPPINGS = {
    "APIConnectorEdit": APIConnectorEdit,
    "ReplicateSeedream45Edit": ReplicateSeedream45Edit,
    "SeedreamAspectRatio": SeedreamAspectRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APIConnectorEdit": "API Connector",
    "ReplicateSeedream45Edit": "Replicate Seedream 4.5",
    "SeedreamAspectRatio": "Seedream Aspect Ratio",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
