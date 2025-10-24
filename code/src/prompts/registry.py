"""
프롬프트 레지스트리 클래스
"""

from typing import Dict, List, Optional
from .base import BasePrompt


class PromptRegistry:
    """
    프롬프트 레지스트리
    프롬프트 클래스를 등록하고 조회하는 기능 제공
    """

    def __init__(self):
        """레지스트리 초기화"""
        self._prompts: Dict[str, BasePrompt] = {}

    def register(self, prompt: BasePrompt) -> None:
        """
        프롬프트 등록

        Args:
            prompt: 등록할 프롬프트 인스턴스
        """
        self._prompts[prompt.name] = prompt

    def get(self, name: str) -> Optional[BasePrompt]:
        """
        프롬프트 조회

        Args:
            name: 프롬프트 이름

        Returns:
            BasePrompt: 프롬프트 인스턴스 또는 None
        """
        return self._prompts.get(name)

    def list_prompts(self) -> List[str]:
        """
        사용 가능한 프롬프트 목록 반환

        Returns:
            List[str]: 프롬프트 이름 목록
        """
        return list(self._prompts.keys())

    def __contains__(self, name: str) -> bool:
        """
        프롬프트 존재 여부 확인

        Args:
            name: 프롬프트 이름

        Returns:
            bool: 존재 여부
        """
        return name in self._prompts


# 전역 레지스트리 인스턴스
_global_registry = PromptRegistry()


def get_registry() -> PromptRegistry:
    """
    전역 레지스트리 인스턴스 반환

    Returns:
        PromptRegistry: 전역 레지스트리
    """
    return _global_registry


def register_default_prompts() -> None:
    """
    기본 프롬프트들을 레지스트리에 자동 등록
    """
    from .baseline import BaselinePrompt
    from .baseline_plus_3examples import BaselinePlus3ExamplesPrompt
    from .baseline_strict import BaselineStrictPrompt
    from .baseline_strict_v2 import BaselineStrictV2Prompt
    from .baseline_spacing import BaselineSpacingPrompt
    from .baseline_josa import BaselineJosaPrompt
    from .fewshot_v2 import FewshotV2Prompt
    from .fewshot_v3 import FewShotV3Prompt
    from .fewshot_v3_enhanced import FewShotV3EnhancedPrompt
    from .fewshot_v3_improved import FewShotV3ImprovedPrompt
    from .errortypes_v3 import ErrorTypesV3Prompt
    from .zero_shot import ZeroShotPrompt

    registry = get_registry()
    registry.register(BaselinePrompt())
    registry.register(BaselinePlus3ExamplesPrompt())
    registry.register(BaselineStrictPrompt())
    registry.register(BaselineStrictV2Prompt())
    registry.register(BaselineSpacingPrompt())
    registry.register(BaselineJosaPrompt())
    registry.register(FewshotV2Prompt())
    registry.register(FewShotV3Prompt())
    registry.register(FewShotV3EnhancedPrompt())
    registry.register(FewShotV3ImprovedPrompt())
    registry.register(ErrorTypesV3Prompt())
    registry.register(ZeroShotPrompt())
