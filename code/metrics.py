"""
평가 지표 모듈 (레거시 래퍼)

하위 호환성을 위한 래퍼 모듈입니다.
실제 구현은 src/metrics/ 모듈에 있습니다.
"""

from src.metrics.lcs import (
    tokenize,
    lcs_table,
    find_lcs,
    find_differences_with_offsets
)

from src.metrics.evaluator import evaluate_correction

__all__ = [
    'tokenize',
    'lcs_table',
    'find_lcs',
    'find_differences_with_offsets',
    'evaluate_correction'
] 