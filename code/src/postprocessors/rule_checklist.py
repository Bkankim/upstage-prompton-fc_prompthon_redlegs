"""
Rule-Checklist 후처리 모듈
국립국어원 규칙 기반의 명확한 교정 규칙 적용
"""

import re
import logging
from typing import Optional

from .base import BasePostprocessor

# 로거 설정
logger = logging.getLogger(__name__)


class RuleChecklistPostprocessor(BasePostprocessor):
    """
    Rule-Checklist 기반 후처리 클래스
    프롬프트 응답에 대한 정제 및 명확한 문법 규칙 적용
    """

    @property
    def name(self) -> str:
        """후처리 모듈 이름 반환"""
        return "rule_checklist"

    def process(self, original: str, corrected: str) -> str:
        """
        Rule-Checklist 후처리 수행

        Args:
            original: 원문 텍스트
            corrected: 모델이 생성한 교정문

        Returns:
            str: 정제된 교정문 (실패 시 원문)
        """
        try:
            # None이나 빈 값 처리
            if not corrected or not isinstance(corrected, str):
                return original

            # 1단계: 응답 정제 (프롬프트 메타데이터 제거)
            text = self._clean_response(corrected)

            # 빈 문자열이 되었다면 원문 반환
            if not text.strip():
                return original

            # 2단계: 문법 규칙 적용 (콜론 로직 개선 후 재활성화)
            text = self._apply_grammar_rules(text)

            # 3단계: 공백 및 줄바꿈 정리
            text = self._clean_whitespace(text)

            # 4단계: 길이 가드 적용 (60% 미만 손실 방지)
            text = self._apply_length_guard(original, text)

            # 최종 결과가 비어있으면 원문 반환
            return text.strip() if text.strip() else original

        except Exception as e:
            # 예외 발생 시 안전하게 원문 반환
            logger.warning(f"Postprocessing failed - {e}")
            return original

    def _clean_response(self, text: str) -> str:
        """
        응답 정제: 프롬프트 메타데이터 제거

        Args:
            text: 원본 응답 텍스트

        Returns:
            str: 정제된 텍스트
        """
        # 레이블 제거 (교정:, 수정:, 결과: 등)
        text = re.sub(r'^(교정|수정|결과|답변|정답)\s*[:：]\s*', '', text, flags=re.MULTILINE)

        # 번호 리스트 제거 (1., 2., -, * 등으로 시작하는 줄)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 번호 리스트나 불릿 포인트로 시작하지 않는 줄만 유지
            if not re.match(r'^\s*[\d\-\*\.]+\s+', line):
                cleaned_lines.append(line)

        # 줄바꿈 유지하며 재결합
        text = '\n'.join(cleaned_lines)

        # 따옴표 제거 (처음과 끝의 따옴표만)
        text = re.sub(r'^["\'「『](.*)["\'」』]$', r'\1', text.strip())

        # XML/HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)

        # "원문 : 교정문" 형식 처리
        # 예: "원문입니다. : 교정된 문장입니다."
        # 콜론 뒤 부분만 추출
        # 주의: 비율(7:3), 시간(3:00) 등 정상 콜론은 제외
        if ':' in text or '：' in text:
            # 비율/시간 패턴이 있으면 스킵
            if not re.search(r'\d+\s*[：:]\s*\d+', text):
                # 메타데이터 콜론 확인: 앞부분(30% 이내)에 키워드 존재
                colon_pos = text.find(':')
                if colon_pos < 0:
                    colon_pos = text.find('：')

                if colon_pos > 0 and colon_pos / len(text) < 0.3:
                    before_colon = text[:colon_pos].strip()
                    keywords = ['원문', '교정', '수정', '결과', '답변', '정답']
                    if any(kw in before_colon for kw in keywords):
                        # 메타데이터로 판단 - 콜론 뒤 부분만 추출
                        parts = re.split(r'\s*[：:]\s*', text, maxsplit=1)
                        if len(parts) == 2:
                            text = parts[1]

        # 괄호 안 설명문 제거 (※, 주의, 참고 등)
        # 예: "(※ 원문의 맞춤법과 문법이...)"
        text = re.sub(r'\s*\([※주참].+?\)', '', text)
        text = re.sub(r'\s*\(원문.+?\)', '', text)
        text = re.sub(r'\s*\(수정.+?\)', '', text)
        text = re.sub(r'\s*\(교정.+?\)', '', text)
        text = re.sub(r'\s*\(예:.+?\)', '', text)

        # ** 강조 문구 제거
        # 예: "**수정 사항 없음**"
        text = re.sub(r'\*\*[^*]+\*\*', '', text)

        # 기타 설명 문구 제거
        text = re.sub(r'수정\s*사항\s*없음', '', text, flags=re.IGNORECASE)
        text = re.sub(r'수정\s*불필요', '', text, flags=re.IGNORECASE)
        text = re.sub(r'교정\s*불필요', '', text, flags=re.IGNORECASE)
        text = re.sub(r'이미\s*정확', '', text, flags=re.IGNORECASE)

        return text

    def _apply_grammar_rules(self, text: str) -> str:
        """
        명확한 문법 규칙 적용

        Args:
            text: 입력 텍스트

        Returns:
            str: 규칙이 적용된 텍스트
        """
        # 규칙 1: '되/돼' 활용 규칙
        # "되어요"의 준말은 "돼요", "되어서"의 준말은 "돼서"
        text = re.sub(r'(?<![가-힣])되요(?![가-힣])', '돼요', text)
        text = re.sub(r'(?<![가-힣])되서(?![가-힣])', '돼서', text)
        text = re.sub(r'되여요', '돼요', text)
        text = re.sub(r'되여서', '돼서', text)

        # 규칙 2: '안 돼' 띄어쓰기
        # 동사 부정은 띄어씀
        text = re.sub(r'안돼요', '안 돼요', text)
        text = re.sub(r'안돼서', '안 돼서', text)
        text = re.sub(r'안된다(?![가-힣])', '안 된다', text)
        text = re.sub(r'안돼(?![가-힣])', '안 돼', text)

        # 규칙 3: '-ㄹ 수 있다' 띄어쓰기
        # '수'는 의존 명사로 반드시 띄어씀
        text = re.sub(r'([가-힣])수있다', r'\1 수 있다', text)
        text = re.sub(r'([가-힣])수있어', r'\1 수 있어', text)
        text = re.sub(r'([가-힣])수있어요', r'\1 수 있어요', text)
        text = re.sub(r'([가-힣])수있습니다', r'\1 수 있습니다', text)
        text = re.sub(r'([가-힣])수없다', r'\1 수 없다', text)
        text = re.sub(r'([가-힣])수없어', r'\1 수 없어', text)
        text = re.sub(r'([가-힣])수없어요', r'\1 수 없어요', text)
        text = re.sub(r'([가-힣])수없습니다', r'\1 수 없습니다', text)

        # 규칙 4: 보조 용언 띄어쓰기
        # '-아/어 보다'는 원칙적으로 띄어씀
        text = re.sub(r'해보다(?![가-힣])', '해 보다', text)
        text = re.sub(r'해보았', '해 보았', text)
        text = re.sub(r'해보았다', '해 보았다', text)
        text = re.sub(r'해보았어', '해 보았어', text)
        text = re.sub(r'해봤', '해 봤', text)
        text = re.sub(r'해봤다', '해 봤다', text)
        text = re.sub(r'해봤어', '해 봤어', text)
        text = re.sub(r'해봐요', '해 봐요', text)
        text = re.sub(r'해봐(?![가-힣])', '해 봐', text)
        text = re.sub(r'해보자', '해 보자', text)

        return text

    def _clean_whitespace(self, text: str) -> str:
        """
        공백 및 줄바꿈 정리

        Args:
            text: 입력 텍스트

        Returns:
            str: 공백이 정리된 텍스트
        """
        # 줄바꿈을 공백으로 변환
        text = text.replace('\n', ' ')

        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)

        # 앞뒤 공백 제거
        text = text.strip()

        return text

    def _apply_length_guard(
        self,
        original: str,
        corrected: str,
        threshold: float = 0.6
    ) -> str:
        """
        길이 가드 적용: 과도한 텍스트 손실 방지

        후처리 결과가 원문 대비 60% 미만으로 줄어든 경우 원문 반환.
        이는 "7:3" → "3" 같은 심각한 손실을 방지합니다.

        Args:
            original: 원본 텍스트
            corrected: 후처리된 텍스트
            threshold: 길이 임계값 (기본 0.6 = 60%)

        Returns:
            str: 가드 적용된 텍스트 (원문 또는 교정문)
        """
        # 원문이 비어있으면 그대로 반환
        if not original or len(original) == 0:
            return corrected

        # 길이 비율 계산
        length_ratio = len(corrected) / len(original)

        # 60% 미만으로 줄어든 경우 원문 반환
        if length_ratio < threshold:
            logger.warning(
                f"Length guard activated: {length_ratio:.1%} "
                f"({len(original)} → {len(corrected)}). "
                f"Returning original text."
            )
            return original

        # 정상 범위면 교정문 반환
        return corrected
