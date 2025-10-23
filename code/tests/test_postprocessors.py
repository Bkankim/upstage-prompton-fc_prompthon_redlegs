"""
Postprocessor 모듈 단위 테스트
Rule-Checklist 후처리 기능 검증
"""

import pytest
from src.postprocessors.base import BasePostprocessor
from src.postprocessors.rule_checklist import RuleChecklistPostprocessor


class TestBasePostprocessor:
    """BasePostprocessor 추상 클래스 테스트"""

    def test_base_is_abstract(self):
        """추상 클래스는 직접 인스턴스화 불가"""
        with pytest.raises(TypeError):
            BasePostprocessor()

    def test_base_requires_name_property(self):
        """하위 클래스는 name 프로퍼티 구현 필수"""
        class IncompleteProcessor(BasePostprocessor):
            def process(self, original, corrected):
                return corrected

        with pytest.raises(TypeError):
            IncompleteProcessor()

    def test_base_requires_process_method(self):
        """하위 클래스는 process 메서드 구현 필수"""
        class IncompleteProcessor(BasePostprocessor):
            @property
            def name(self):
                return "test"

        with pytest.raises(TypeError):
            IncompleteProcessor()


class TestRuleChecklistPostprocessor:
    """RuleChecklistPostprocessor 기능 테스트"""

    @pytest.fixture
    def processor(self):
        """테스트용 프로세서 인스턴스"""
        return RuleChecklistPostprocessor()

    # 1. 되/돼 활용 규칙 테스트
    def test_dwae_rule_dweyo(self, processor):
        """'되요' → '돼요' 교정"""
        result = processor.process("원문", "되요")
        assert result == "돼요"

    def test_dwae_rule_dweseo(self, processor):
        """'되서' → '돼서' 교정"""
        result = processor.process("원문", "되서")
        assert result == "돼서"

    def test_dwae_rule_dweyo_variant(self, processor):
        """'되여요' → '돼요' 교정"""
        result = processor.process("원문", "되여요")
        assert result == "돼요"

    def test_dwae_rule_dweseo_variant(self, processor):
        """'되여서' → '돼서' 교정"""
        result = processor.process("원문", "되여서")
        assert result == "돼서"

    # 2. 안 돼 띄어쓰기 테스트
    def test_spacing_andwaeyo(self, processor):
        """'안돼요' → '안 돼요' 교정"""
        result = processor.process("원문", "안돼요")
        assert result == "안 돼요"

    def test_spacing_andwaeseo(self, processor):
        """'안돼서' → '안 돼서' 교정"""
        result = processor.process("원문", "안돼서")
        assert result == "안 돼서"

    def test_spacing_andoenda(self, processor):
        """'안된다' → '안 된다' 교정"""
        result = processor.process("원문", "안된다")
        assert result == "안 된다"

    def test_spacing_andwae(self, processor):
        """'안돼' → '안 돼' 교정"""
        result = processor.process("원문", "안돼")
        assert result == "안 돼"

    # 3. 할 수 있다 띄어쓰기 테스트
    def test_spacing_hal_su_itda(self, processor):
        """'할수있다' → '할 수 있다' 교정"""
        result = processor.process("원문", "할수있다")
        assert result == "할 수 있다"

    def test_spacing_hal_su_isseoyo(self, processor):
        """'할수있어요' → '할 수 있어요' 교정"""
        result = processor.process("원문", "할수있어요")
        assert result == "할 수 있어요"

    def test_spacing_hal_su_eopda(self, processor):
        """'할수없다' → '할 수 없다' 교정"""
        result = processor.process("원문", "할수없다")
        assert result == "할 수 없다"

    def test_spacing_hal_su_eopseoyo(self, processor):
        """'할수없어요' → '할 수 없어요' 교정"""
        result = processor.process("원문", "할수없어요")
        assert result == "할 수 없어요"

    # 4. 보조 용언 띄어쓰기 테스트
    def test_spacing_haeboda(self, processor):
        """'해보다' → '해 보다' 교정"""
        result = processor.process("원문", "해보다")
        assert result == "해 보다"

    def test_spacing_haeboatda(self, processor):
        """'해보았다' → '해 보았다' 교정"""
        result = processor.process("원문", "해보았다")
        assert result == "해 보았다"

    def test_spacing_haebwayo(self, processor):
        """'해봐요' → '해 봐요' 교정"""
        result = processor.process("원문", "해봐요")
        assert result == "해 봐요"

    def test_spacing_haeboja(self, processor):
        """'해보자' → '해 보자' 교정"""
        result = processor.process("원문", "해보자")
        assert result == "해 보자"

    # 5. 응답 정제 테스트 (메타데이터 제거)
    def test_remove_label_gyojeong(self, processor):
        """'교정:' 레이블 제거"""
        result = processor.process("원문", "교정: 교정된 문장")
        assert result == "교정된 문장"

    def test_remove_label_sujung(self, processor):
        """'수정:' 레이블 제거"""
        result = processor.process("원문", "수정: 수정된 문장")
        assert result == "수정된 문장"

    def test_remove_label_gyeolgwa(self, processor):
        """'결과:' 레이블 제거"""
        result = processor.process("원문", "결과: 결과 문장")
        assert result == "결과 문장"

    def test_remove_numbering(self, processor):
        """번호 리스트 제거 (1., 2. 등)"""
        result = processor.process("원문", "1. 첫 번째 문장")
        assert result == "첫 번째 문장"

    def test_remove_quotes_double(self, processor):
        """큰따옴표 제거"""
        result = processor.process("원문", '"교정된 문장"')
        assert result == "교정된 문장"

    def test_remove_quotes_single(self, processor):
        """작은따옴표 제거"""
        result = processor.process("원문", "'교정된 문장'")
        assert result == "교정된 문장"

    def test_remove_xml_tags(self, processor):
        """XML/HTML 태그 제거"""
        result = processor.process("원문", "<correction>교정된 문장</correction>")
        assert result == "교정된 문장"

    # 6. 공백 및 줄바꿈 정리 테스트
    def test_normalize_newlines(self, processor):
        """줄바꿈을 공백으로 변환"""
        result = processor.process("원문", "첫 줄\n두 번째 줄")
        assert result == "첫 줄 두 번째 줄"

    def test_normalize_multiple_spaces(self, processor):
        """연속된 공백을 하나로"""
        result = processor.process("원문", "여러    공백    있음")
        assert result == "여러 공백 있음"

    # 7. 엣지 케이스 테스트
    def test_empty_response_fallback(self, processor):
        """빈 응답 시 원문 반환"""
        result = processor.process("원문입니다", "")
        assert result == "원문입니다"

    def test_whitespace_only_fallback(self, processor):
        """공백만 있는 경우 원문 반환"""
        result = processor.process("원문입니다", "   \n  ")
        assert result == "원문입니다"

    def test_identical_text_passthrough(self, processor):
        """원문과 동일한 경우 그대로 반환"""
        original = "완벽한 문장입니다"
        corrected = "완벽한 문장입니다"
        result = processor.process(original, corrected)
        assert result == original

    def test_none_original_safe(self, processor):
        """원문이 None인 경우 안전 처리"""
        result = processor.process(None, "교정된 문장")
        assert result == "교정된 문장"

    def test_none_corrected_safe(self, processor):
        """교정문이 None인 경우 원문 반환"""
        result = processor.process("원문입니다", None)
        assert result == "원문입니다"

    # 8. 복합 규칙 테스트
    def test_combined_rules_1(self, processor):
        """복합 규칙: 되요 + 안돼요"""
        result = processor.process("원문", "되요 안돼요")
        assert result == "돼요 안 돼요"

    def test_combined_rules_2(self, processor):
        """복합 규칙: 할수있어요 + 해보자"""
        result = processor.process("원문", "할수있어요 해보자")
        assert result == "할 수 있어요 해 보자"

    def test_combined_rules_3(self, processor):
        """복합 규칙: 레이블 + 복합 오류"""
        result = processor.process("원문", "교정: 되요 할수있어요")
        assert result == "돼요 할 수 있어요"

    def test_combined_rules_4(self, processor):
        """복합 규칙: 따옴표 + 복합 오류"""
        result = processor.process("원문", '"되서 안돼요"')
        assert result == "돼서 안 돼요"

    def test_combined_rules_5(self, processor):
        """복합 규칙: 모든 규칙 적용"""
        result = processor.process(
            "원문",
            '교정: "되여요   안돼요\n할수없어요   해보았다"'
        )
        assert result == "돼요 안 돼요 할 수 없어요 해 보았다"

    # 9. 실제 사용 시나리오 테스트
    def test_realistic_scenario_1(self, processor):
        """실제 시나리오: 프롬프트 응답 정제"""
        response = """
        교정: 이 문제는 되요? 안돼요.
        할수있다면 해보자.
        """
        result = processor.process("원문", response)
        expected = "이 문제는 돼요? 안 돼요. 할 수 있다면 해 보자."
        assert result == expected

    def test_realistic_scenario_2(self, processor):
        """실제 시나리오: 번호 리스트 응답"""
        response = "1. 되서 안돼요"
        result = processor.process("원문", response)
        assert result == "돼서 안 돼요"

    def test_realistic_scenario_3(self, processor):
        """실제 시나리오: 설명이 포함된 응답"""
        response = "되요. 이것은 맞춤법 오류입니다. 보조 용언은 띄어 씁니다."
        result = processor.process("원문", response)
        # 첫 문장만 추출하지만, 규칙은 적용됨
        assert "돼요" in result

    # 10. 속성 테스트
    def test_processor_name(self, processor):
        """프로세서 이름 확인"""
        assert processor.name == "rule_checklist"

    def test_processor_is_instance_of_base(self, processor):
        """BasePostprocessor의 인스턴스 확인"""
        assert isinstance(processor, BasePostprocessor)


class TestIntegration:
    """통합 테스트 (Generator와의 연동은 별도 테스트)"""

    def test_multiple_processors_can_coexist(self):
        """여러 프로세서 인스턴스 동시 사용 가능"""
        p1 = RuleChecklistPostprocessor()
        p2 = RuleChecklistPostprocessor()

        result1 = p1.process("원문", "되요")
        result2 = p2.process("원문", "안돼요")

        assert result1 == "돼요"
        assert result2 == "안 돼요"

    def test_processor_is_stateless(self):
        """프로세서는 상태를 가지지 않음 (순수 함수)"""
        processor = RuleChecklistPostprocessor()

        # 같은 입력은 항상 같은 출력
        result1 = processor.process("원문", "되요")
        result2 = processor.process("원문", "되요")
        result3 = processor.process("원문", "되요")

        assert result1 == result2 == result3 == "돼요"
