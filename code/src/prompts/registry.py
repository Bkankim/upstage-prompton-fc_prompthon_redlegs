"""
프롬프트 레지스트리 - 간소화 버전

scripts에서 프롬프트 클래스를 이름으로 조회할 수 있도록 하는 레지스트리
"""

from typing import Dict, Type
from .base import BasePrompt
from .baseline import BaselinePrompt
from .zero_shot import ZeroShotPrompt
from .baseline_josa import BaselineJosaPrompt
from .baseline_plus_3examples import BaselinePlus3ExamplesPrompt


# 프롬프트 레지스트리 (이름 → 클래스 매핑)
_REGISTRY: Dict[str, Type[BasePrompt]] = {}


def register_default_prompts():
    """
    기본 프롬프트를 레지스트리에 등록

    등록되는 프롬프트:
    - baseline: BaselinePrompt (맞춤법 1개 예시, 최고 성능)
    - zero_shot: ZeroShotPrompt (예시 0개)
    - baseline_josa: BaselineJosaPrompt (조사 1개 예시)
    - baseline_plus_3examples: BaselinePlus3ExamplesPrompt (4개 예시)
    """
    _REGISTRY['baseline'] = BaselinePrompt
    _REGISTRY['zero_shot'] = ZeroShotPrompt
    _REGISTRY['baseline_josa'] = BaselineJosaPrompt
    _REGISTRY['baseline_plus_3examples'] = BaselinePlus3ExamplesPrompt


def get_registry() -> Dict[str, Type[BasePrompt]]:
    """
    프롬프트 레지스트리 반환

    Returns:
        Dict[str, Type[BasePrompt]]: 프롬프트 이름 → 클래스 매핑
    """
    if not _REGISTRY:
        register_default_prompts()
    return _REGISTRY
