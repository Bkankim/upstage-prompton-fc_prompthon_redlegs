"""
Prompt module
Provides prompt classes and registry
"""

from .base import BasePrompt
from .baseline import BaselinePrompt
from .baseline_strict import BaselineStrictPrompt
from .baseline_strict_v2 import BaselineStrictV2Prompt
from .fewshot_v2 import FewshotV2Prompt
from .fewshot_v3 import FewShotV3Prompt
from .fewshot_v3_enhanced import FewShotV3EnhancedPrompt
from .errortypes_v3 import ErrorTypesV3Prompt
from .registry import PromptRegistry, get_registry, register_default_prompts

# Auto-register default prompts on module import
register_default_prompts()

__all__ = [
    "BasePrompt",
    "BaselinePrompt",
    "BaselineStrictPrompt",
    "BaselineStrictV2Prompt",
    "FewshotV2Prompt",
    "FewShotV3Prompt",
    "FewShotV3EnhancedPrompt",
    "ErrorTypesV3Prompt",
    "PromptRegistry",
    "get_registry",
    "register_default_prompts",
]
