"""
Prompt module
Provides prompt classes and registry
"""

from .base import BasePrompt
from .baseline import BaselinePrompt
from .fewshot_v2 import FewshotV2Prompt
from .errortypes_v3 import ErrorTypesV3Prompt
from .registry import PromptRegistry, get_registry, register_default_prompts

# Auto-register default prompts on module import
register_default_prompts()

__all__ = [
    "BasePrompt",
    "BaselinePrompt",
    "FewshotV2Prompt",
    "ErrorTypesV3Prompt",
    "PromptRegistry",
    "get_registry",
    "register_default_prompts",
]
