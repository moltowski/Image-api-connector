from .api_connector import APIConnectorEdit, SeedreamAspectRatio

NODE_CLASS_MAPPINGS = {
    "APIConnectorEdit": APIConnectorEdit,
    "SeedreamAspectRatio": SeedreamAspectRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APIConnectorEdit": "API Connector",
    "SeedreamAspectRatio": "Seedream Aspect Ratio",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
