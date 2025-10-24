"""
프롬프트 템플릿 모듈

사용 가능한 프롬프트:
- BaselinePrompt: 맞춤법 1개 예시 (최고 성능)
- ZeroShotPrompt: 예시 0개
- BaselineJosaPrompt: 조사 1개 예시
- BaselinePlus3ExamplesPrompt: 4개 예시
"""

from .base import BasePrompt
from .baseline import BaselinePrompt
from .zero_shot import ZeroShotPrompt
from .baseline_josa import BaselineJosaPrompt
from .baseline_plus_3examples import BaselinePlus3ExamplesPrompt

__all__ = [
    'BasePrompt',
    'BaselinePrompt',
    'ZeroShotPrompt',
    'BaselineJosaPrompt',
    'BaselinePlus3ExamplesPrompt',
]
