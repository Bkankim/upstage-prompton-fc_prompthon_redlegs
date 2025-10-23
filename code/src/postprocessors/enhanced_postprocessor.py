"""
Enhanced 후처리 모듈

전문가 조언 반영:
- 메타데이터 제거 필터 강화
- 반복 문장 탐지 및 제거
- 숫자/단위 원문 되돌림
- 처리 전/후 로깅
- 함수 단위 테스트 지원
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .base import BasePostprocessor

# 로거 설정
logger = logging.getLogger(__name__)


class EnhancedPostprocessor(BasePostprocessor):
    """
    강화된 후처리 클래스

    기존 rule_checklist 기능 + 추가 기능:
    - 메타데이터 제거 강화 (※, 최종, 원칙, [...] 등)
    - 반복 문장 탐지 및 제거
    - 숫자/단위 원문 되돌림 (변경되면 안 되는 경우)
    - 처리 전/후 로깅 (비교 분석용)
    """

    def __init__(self, enable_logging: bool = True):
        """
        Enhanced 후처리 초기화

        Args:
            enable_logging: 처리 전/후 로깅 활성화 여부
        """
        self.enable_logging = enable_logging
        self.processing_log: List[Dict] = []

    @property
    def name(self) -> str:
        """후처리 모듈 이름 반환"""
        return "enhanced"

    def process(self, original: str, corrected: str) -> str:
        """
        Enhanced 후처리 수행

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

            # 처리 전 상태 저장
            before_postprocess = corrected

            # 1단계: 메타데이터 제거 (강화)
            text = self._clean_metadata_enhanced(corrected)

            # 2단계: 반복 문장 탐지 및 제거
            text = self._remove_repeated_sentences(text)

            # 3단계: 응답 정제 (기존 로직)
            text = self._clean_response(text)

            # 4단계: 문법 규칙 적용
            text = self._apply_grammar_rules(text)

            # 5단계: 공백 및 줄바꿈 정리
            text = self._clean_whitespace(text)

            # 6단계: 숫자/단위 원문 되돌림
            text = self._restore_numbers_and_units(original, text)

            # 7단계: 길이 가드 적용 (60% 미만 손실 방지)
            text = self._apply_length_guard(original, text)

            # 처리 후 상태 저장
            after_postprocess = text

            # 로깅 (옵션)
            if self.enable_logging:
                self._log_processing(
                    original, before_postprocess, after_postprocess
                )

            # 최종 결과가 비어있으면 원문 반환
            return text.strip() if text.strip() else original

        except Exception as e:
            # 예외 발생 시 안전하게 원문 반환
            logger.warning(f"Enhanced postprocessing failed - {e}")
            return original

    def _clean_metadata_enhanced(self, text: str) -> str:
        """
        메타데이터 제거 강화 (화이트리스트 추가)

        기존 로직 + 추가 패턴 + 화이트리스트

        개선 사항:
        - 화이트리스트: 정상 표현 보호 ("참고할 만하다", "설명되기 어렵다")
        - 컨텍스트 기반 패턴

        Args:
            text: 원본 응답 텍스트

        Returns:
            str: 메타데이터가 제거된 텍스트
        """
        # 화이트리스트: 정상 표현 (임시 보호)
        whitelist_patterns = {
            '__REF1__': r'참고할\s*(만하다|필요|가능)',
            '__EXPL1__': r'설명(되기|하기)\s*(어렵|쉬|가능)',
            '__REF2__': r'참고\s*문헌',
            '__EXPL2__': r'설명\s*자료',
        }

        # 임시 치환 (보호)
        whitelist_backup = {}
        for placeholder, pattern in whitelist_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                # 첫 번째 매치를 문자열로 저장 (튜플인 경우 첫 요소)
                first_match = matches[0] if isinstance(matches[0], str) else ''.join(matches[0])
                text = re.sub(pattern, placeholder, text, count=1)
                whitelist_backup[placeholder] = first_match

        # 패턴 1: ※ 문구 제거
        text = re.sub(r'※[^\n]*', '', text)

        # 패턴 2: [...] 형태 레이블 제거
        text = re.sub(r'\[[^\]]*최종[^\]]*\]', '', text)
        text = re.sub(r'\[[^\]]*시스템[^\]]*\]', '', text)
        text = re.sub(r'\[[^\]]*오류[^\]]*\]', '', text)
        text = re.sub(r'\[[^\]]*답변[^\]]*\]', '', text)

        # 패턴 3: 컨텍스트 기반 메타데이터 키워드
        # "지시사항을 따라", "규칙을 준수" 등 (단순 단어는 제외)
        metadata_keywords = [
            r'지시사항[을를]?\s*(따라|준수)',
            r'규칙[을를]?\s*(따라|준수)',
            r'원칙\s*\d*\s*[:：]',
            r'규칙\s*\d*\s*[:：]',
            r'수정\s*사항\s*[:：]',
            r'원칙\s*적용',
            r'원칙\s*준수',
            r'오류\s*재확인',
            r'요구사항\s*충족',
            r'추가.*설명[을를]?\s*제공',
        ]
        for keyword in metadata_keywords:
            text = re.sub(keyword, '', text, flags=re.IGNORECASE)

        # 패턴 4: 연속된 "다" 제거 (오류 패턴)
        text = re.sub(r'다\[', '', text)
        text = re.sub(r'다최종', '', text)
        text = re.sub(r'다원칙', '', text)

        # 패턴 5: "교정:", "수정:", "결과:" 등 레이블
        text = re.sub(
            r'^(교정|수정|결과|답변|정답|최종)\s*[:：]\s*',
            '',
            text,
            flags=re.MULTILINE
        )

        # 화이트리스트 복원
        for placeholder, original in whitelist_backup.items():
            text = text.replace(placeholder, original)

        return text

    def _remove_repeated_sentences(self, text: str) -> str:
        """
        반복 문장 탐지 및 제거 (강화 버전)

        같은 문장이 여러 번 출현하는 경우 첫 번째만 유지.
        괄호, 특수문자로 시작하는 중복도 탐지.

        개선 사항:
        - 괄호로 시작하는 중복 탐지 (예: "문장A. ( 문장A.")
        - 부분 매칭 대신 완전 매칭
        - 공백, 괄호 무시하고 비교

        Args:
            text: 입력 텍스트

        Returns:
            str: 반복이 제거된 텍스트
        """
        # 1단계: 괄호로 시작하는 중복 패턴 제거
        # 예: "문장A. ( 문장A." → "문장A."
        text = re.sub(r'\.\s*\(\s*([^.!?]+)\.\s*\1', r'. \1', text)

        # 2단계: 문장 분리 (마침표, 느낌표, 물음표 기준)
        sentences = re.split(r'([.!?])', text)

        # 문장과 구분자를 다시 결합
        combined_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sent = sentences[i] + sentences[i + 1]
                combined_sentences.append(sent.strip())

        # 3단계: 중복 제거 (강화)
        seen = set()
        unique_sentences = []

        for sent in combined_sentences:
            # 정규화: 공백, 괄호, 특수문자 제거 후 비교
            normalized = re.sub(r'[\s()\[\]{}]', '', sent)
            normalized = re.sub(r'[※：:\-]', '', normalized)

            # 빈 문장은 건너뛰기
            if not normalized:
                continue

            # 이미 본 문장은 건너뛰기
            if normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sent)

        # 4단계: 재결합
        result = ' '.join(unique_sentences)

        # 중복 제거 로깅
        removed_count = len(combined_sentences) - len(unique_sentences)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} repeated sentences")

        return result

    def _clean_response(self, text: str) -> str:
        """
        응답 정제: 프롬프트 메타데이터 제거 (기존 로직)

        Args:
            text: 원본 응답 텍스트

        Returns:
            str: 정제된 텍스트
        """
        # 레이블 제거 (교정:, 수정:, 결과: 등)
        text = re.sub(
            r'^(교정|수정|결과|답변|정답)\s*[:：]\s*',
            '',
            text,
            flags=re.MULTILINE
        )

        # 번호 리스트 제거
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not re.match(r'^\s*[\d\-\*\.]+\s+', line):
                cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)

        # 따옴표 제거
        text = re.sub(r'^["\'「『](.*)["\'」』]$', r'\1', text.strip())

        # XML/HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)

        # "원문 : 교정문" 형식 처리
        if ':' in text or '：' in text:
            if not re.search(r'\d+\s*[：:]\s*\d+', text):
                colon_pos = text.find(':')
                if colon_pos < 0:
                    colon_pos = text.find('：')

                if colon_pos > 0 and colon_pos / len(text) < 0.3:
                    before_colon = text[:colon_pos].strip()
                    keywords = ['원문', '교정', '수정', '결과', '답변', '정답']
                    if any(kw in before_colon for kw in keywords):
                        parts = re.split(r'\s*[：:]\s*', text, maxsplit=1)
                        if len(parts) == 2:
                            text = parts[1]

        # 괄호 안 설명문 제거
        text = re.sub(r'\s*\([※주참].+?\)', '', text)
        text = re.sub(r'\s*\(원문.+?\)', '', text)
        text = re.sub(r'\s*\(수정.+?\)', '', text)
        text = re.sub(r'\s*\(교정.+?\)', '', text)
        text = re.sub(r'\s*\(예:.+?\)', '', text)

        # ** 강조 문구 제거
        text = re.sub(r'\*\*[^*]+\*\*', '', text)

        # 기타 설명 문구 제거
        text = re.sub(r'수정\s*사항\s*없음', '', text, flags=re.IGNORECASE)
        text = re.sub(r'수정\s*불필요', '', text, flags=re.IGNORECASE)
        text = re.sub(r'교정\s*불필요', '', text, flags=re.IGNORECASE)
        text = re.sub(r'이미\s*정확', '', text, flags=re.IGNORECASE)

        return text

    def _apply_grammar_rules(self, text: str) -> str:
        """
        명확한 문법 규칙 적용 (기존 로직)

        Args:
            text: 입력 텍스트

        Returns:
            str: 규칙이 적용된 텍스트
        """
        # 규칙 1: '되/돼' 활용 규칙
        text = re.sub(r'(?<![가-힣])되요(?![가-힣])', '돼요', text)
        text = re.sub(r'(?<![가-힣])되서(?![가-힣])', '돼서', text)
        text = re.sub(r'되여요', '돼요', text)
        text = re.sub(r'되여서', '돼서', text)

        # 규칙 2: '안 돼' 띄어쓰기
        text = re.sub(r'안돼요', '안 돼요', text)
        text = re.sub(r'안돼서', '안 돼서', text)
        text = re.sub(r'안된다(?![가-힣])', '안 된다', text)
        text = re.sub(r'안돼(?![가-힣])', '안 돼', text)

        # 규칙 3: '-ㄹ 수 있다' 띄어쓰기
        text = re.sub(r'([가-힣])수있다', r'\1 수 있다', text)
        text = re.sub(r'([가-힣])수있어', r'\1 수 있어', text)
        text = re.sub(r'([가-힣])수있어요', r'\1 수 있어요', text)
        text = re.sub(r'([가-힣])수있습니다', r'\1 수 있습니다', text)
        text = re.sub(r'([가-힣])수없다', r'\1 수 없다', text)
        text = re.sub(r'([가-힣])수없어', r'\1 수 없어', text)
        text = re.sub(r'([가-힣])수없어요', r'\1 수 없어요', text)
        text = re.sub(r'([가-힣])수없습니다', r'\1 수 없습니다', text)

        # 규칙 4: 보조 용언 띄어쓰기
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
        공백 및 줄바꿈 정리 (기존 로직)

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

    def _restore_numbers_and_units(
        self,
        original: str,
        corrected: str
    ) -> str:
        """
        숫자/단위 원문 되돌림 (소수점 예외 처리 추가)

        특정 패턴의 숫자/단위가 원문과 다르게 변경된 경우
        원문 값으로 되돌림. 신중하게 적용.

        복원 대상:
        - 숫자 단위 (10만명, 160cm~170cm 등)
        - 비율/시간 (7:3, 19:30 등)
        - 소수점 (1.4% → "1. 4%" 방지)

        Args:
            original: 원문 텍스트
            corrected: 교정된 텍스트

        Returns:
            str: 숫자/단위가 복원된 텍스트
        """
        # 패턴 0: 소수점 띄어쓰기 수정 (최우선)
        # "1. 4%" → "1.4%", "42. 67%" → "42.67%"
        corrected = re.sub(r'(\d+)\.\s+(\d+)%', r'\1.\2%', corrected)
        corrected = re.sub(r'(\d+)\.\s+(\d+)([가-힣])', r'\1.\2\3', corrected)

        # 패턴 1: 숫자+단위 (예: 10만명, 186만명)
        number_unit_pattern = r'\d+만?\s*[명개채대권원건명부곡분]'

        # 원문에서 숫자+단위 추출
        original_numbers = re.findall(number_unit_pattern, original)

        # 교정문에서 숫자+단위 추출
        corrected_numbers = re.findall(number_unit_pattern, corrected)

        # 변경된 경우 원문으로 복원
        # (단, 개수가 다르면 복원하지 않음 - 실제 오류일 수 있음)
        if len(original_numbers) == len(corrected_numbers):
            for orig, corr in zip(original_numbers, corrected_numbers):
                if orig != corr:
                    # 복원 로깅
                    logger.info(
                        f"Restoring number/unit: '{corr}' → '{orig}'"
                    )
                    # 첫 출현만 복원
                    corrected = corrected.replace(corr, orig, 1)

        # 패턴 2: 비율/시간 (예: 7:3, 19:30)
        # 단, 소수점과 혼동하지 않도록 주의
        ratio_time_pattern = r'\b\d+\s*:\s*\d+\b'

        # 원문에서 비율/시간 추출
        original_ratios = re.findall(ratio_time_pattern, original)

        # 교정문에서 비율/시간 추출
        corrected_ratios = re.findall(ratio_time_pattern, corrected)

        # 변경된 경우 원문으로 복원
        if len(original_ratios) == len(corrected_ratios):
            for orig, corr in zip(original_ratios, corrected_ratios):
                # 원문과 교정문이 다른 경우만 복원
                orig_norm = re.sub(r'\s', '', orig)
                corr_norm = re.sub(r'\s', '', corr)
                if orig_norm != corr_norm:
                    logger.info(f"Restoring ratio/time: '{corr}' → '{orig}'")
                    corrected = corrected.replace(corr, orig, 1)

        return corrected

    def _apply_length_guard(
        self,
        original: str,
        corrected: str,
        threshold: float = 0.6
    ) -> str:
        """
        길이 가드 적용: 과도한 텍스트 손실 방지 (기존 로직)

        Args:
            original: 원본 텍스트
            corrected: 후처리된 텍스트
            threshold: 길이 임계값 (기본 0.6 = 60%)

        Returns:
            str: 가드 적용된 텍스트
        """
        if not original or len(original) == 0:
            return corrected

        length_ratio = len(corrected) / len(original)

        if length_ratio < threshold:
            logger.warning(
                f"Length guard activated: {length_ratio:.1%} "
                f"({len(original)} → {len(corrected)}). "
                f"Returning original text."
            )
            return original

        return corrected

    def _log_processing(
        self,
        original: str,
        before: str,
        after: str
    ) -> None:
        """
        처리 전/후 로깅 (비교 분석용)

        Args:
            original: 원문
            before: 후처리 전 (모델 출력)
            after: 후처리 후
        """
        log_entry = {
            'original': original,
            'before_postprocess': before,
            'after_postprocess': after,
            'original_length': len(original),
            'before_length': len(before),
            'after_length': len(after),
            'metadata_removed': before != after,
            'length_ratio_before': len(before) / len(original) if original else 0,
            'length_ratio_after': len(after) / len(original) if original else 0,
        }
        self.processing_log.append(log_entry)

    def save_processing_log(self, output_path: str) -> None:
        """
        처리 로그를 JSON 파일로 저장

        Args:
            output_path: 저장 경로 (예: outputs/analysis/postprocess_comparison.json)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_log, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved processing log to {output_file}")

    def get_processing_summary(self) -> Dict:
        """
        처리 로그 요약 통계

        Returns:
            Dict: 요약 통계
        """
        if not self.processing_log:
            return {}

        total = len(self.processing_log)
        metadata_removed_count = sum(
            1 for log in self.processing_log if log['metadata_removed']
        )

        avg_length_ratio_before = sum(
            log['length_ratio_before'] for log in self.processing_log
        ) / total

        avg_length_ratio_after = sum(
            log['length_ratio_after'] for log in self.processing_log
        ) / total

        return {
            'total_cases': total,
            'metadata_removed_count': metadata_removed_count,
            'metadata_removed_rate': metadata_removed_count / total * 100,
            'avg_length_ratio_before': avg_length_ratio_before * 100,
            'avg_length_ratio_after': avg_length_ratio_after * 100,
        }


# 함수 단위 테스트 및 드라이런 지원
def test_enhanced_postprocessor():
    """
    Enhanced 후처리 모듈 단위 테스트
    """
    postprocessor = EnhancedPostprocessor(enable_logging=True)

    # 테스트 케이스 1: 메타데이터 제거
    test_case_1 = {
        'original': '리조트 수요가 급증했다.',
        'corrected': '※ 원칙 준수: 리조트 수요가 급증했다. [최종 출력] 리조트 수요가 급증했다.'
    }
    result_1 = postprocessor.process(
        test_case_1['original'],
        test_case_1['corrected']
    )
    print(f"Test 1 - Metadata removal:")
    print(f"  Input : {test_case_1['corrected']}")
    print(f"  Output: {result_1}")
    print()

    # 테스트 케이스 2: 반복 문장 제거
    test_case_2 = {
        'original': '그가 벽에 부딪혀 넘어졌다.',
        'corrected': '그가 벽에 부딪혀 넘어졌다. 그가 벽에 부딪혀 넘어졌다.'
    }
    result_2 = postprocessor.process(
        test_case_2['original'],
        test_case_2['corrected']
    )
    print(f"Test 2 - Repeated sentences:")
    print(f"  Input : {test_case_2['corrected']}")
    print(f"  Output: {result_2}")
    print()

    # 테스트 케이스 3: 숫자/단위 복원
    test_case_3 = {
        'original': '관광객은 누적 186만명으로, 작년 대비 31% 늘어났다.',
        'corrected': '관광객은 누적 186만 명으로, 작년 대비 31% 늘어났다.'
    }
    result_3 = postprocessor.process(
        test_case_3['original'],
        test_case_3['corrected']
    )
    print(f"Test 3 - Number/unit restoration:")
    print(f"  Input : {test_case_3['corrected']}")
    print(f"  Output: {result_3}")
    print()

    # 요약 통계
    summary = postprocessor.get_processing_summary()
    print("Summary statistics:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # 단위 테스트 실행
    test_enhanced_postprocessor()
