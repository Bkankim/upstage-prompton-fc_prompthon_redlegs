"""
초보수적 규칙 기반 후처리기
Baseline이 교정하지 않은 경우에만 명확한 규칙 적용
"""

import re


class MinimalRulePostprocessor:
    """
    초보수적 규칙 후처리기

    적용 조건:
    - 원문 = Baseline 출력일 때만 적용
    - False Positive ≈ 0%인 규칙만 사용
    - 60% 길이 가드, 150% 길이 가드 적용
    """

    def __init__(self):
        """
        후처리기 초기화
        """
        # 초보수적 규칙 정의 (False Positive ≈ 0%)
        self.rules = [
            # 규칙 1: 금새 → 금세 (100% 확실)
            {
                'name': '금새→금세',
                'pattern': re.compile(r'금새'),
                'replacement': '금세',
                'confidence': 'HIGH'
            },
            # 규칙 2: 치 않 → 지 않 (형용사 뒤, 95%+ 확실)
            {
                'name': '치않→지않',
                'pattern': re.compile(r'([가-힣]+)치\s+(않[가-힣]*)'),
                'replacement': r'\1지 \2',
                'confidence': 'HIGH'
            },
            # 규칙 3: 추측컨대 → 추측건대 (100% 확실)
            {
                'name': '추측컨대→추측건대',
                'pattern': re.compile(r'추측컨대'),
                'replacement': '추측건대',
                'confidence': 'HIGH'
            },
        ]

    def _apply_rules(self, text: str) -> str:
        """
        규칙 적용

        Args:
            text: 입력 텍스트

        Returns:
            str: 규칙 적용 후 텍스트
        """
        result = text

        for rule in self.rules:
            result = rule['pattern'].sub(rule['replacement'], result)

        return result

    def _check_length_guard(self, original: str, corrected: str) -> bool:
        """
        길이 가드 체크

        Args:
            original: 원문
            corrected: 교정된 텍스트

        Returns:
            bool: 길이가 안전 범위 내인지 여부
        """
        original_len = len(original)
        corrected_len = len(corrected)

        if original_len == 0:
            return True

        ratio = corrected_len / original_len

        # 60% 미만 또는 150% 초과 → 위험
        if ratio < 0.6 or ratio > 1.5:
            return False

        return True

    def process(self, original: str, model_output: str) -> str:
        """
        후처리 실행

        Args:
            original: 원문 텍스트
            model_output: 모델 출력 (Baseline)

        Returns:
            str: 후처리된 텍스트
        """
        # 핵심 전략: 원문 = 모델 출력일 때만 규칙 적용
        # (즉, Baseline이 교정하지 않았을 때만)
        if original.strip() != model_output.strip():
            # Baseline이 이미 교정함 → 건드리지 않음
            return model_output

        # 규칙 적용
        corrected = self._apply_rules(original)

        # 규칙 적용 결과가 원문과 동일 → 변경 없음
        if corrected.strip() == original.strip():
            return model_output

        # 길이 가드 체크
        if not self._check_length_guard(original, corrected):
            # 길이 변화가 과도함 → 원문 반환
            return original

        return corrected
