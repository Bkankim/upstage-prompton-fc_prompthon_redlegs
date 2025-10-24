"""
Postprocessor 모듈 단위 테스트
"""

import pytest
from src.postprocessors.base import BasePostprocessor
from src.postprocessors.enhanced_postprocessor import EnhancedPostprocessor
from src.postprocessors.minimal_rule import MinimalRulePostprocessor


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


class TestEnhancedPostprocessor:
    """EnhancedPostprocessor 기능 테스트"""

    @pytest.fixture
    def processor(self):
        """테스트용 프로세서 인스턴스"""
        return EnhancedPostprocessor(enable_logging=False)

    def test_processor_name(self, processor):
        """프로세서 이름 확인"""
        assert processor.name == "enhanced"

    def test_processor_is_instance_of_base(self, processor):
        """BasePostprocessor의 인스턴스 확인"""
        assert isinstance(processor, BasePostprocessor)

    def test_basic_processing(self, processor):
        """기본 처리 테스트"""
        result = processor.process("원문", "교정문")
        assert isinstance(result, str)


class TestMinimalRulePostprocessor:
    """MinimalRulePostprocessor 기능 테스트"""

    @pytest.fixture
    def processor(self):
        """테스트용 프로세서 인스턴스"""
        return MinimalRulePostprocessor()

    def test_processor_name(self, processor):
        """프로세서 이름 확인"""
        assert processor.name == "minimal_rule"

    def test_processor_is_instance_of_base(self, processor):
        """BasePostprocessor의 인스턴스 확인"""
        assert isinstance(processor, BasePostprocessor)

    def test_basic_processing(self, processor):
        """기본 처리 테스트"""
        result = processor.process("원문", "교정문")
        assert isinstance(result, str)


class TestIntegration:
    """통합 테스트"""

    def test_multiple_processors_can_coexist(self):
        """여러 프로세서 인스턴스 동시 사용 가능"""
        p1 = EnhancedPostprocessor(enable_logging=False)
        p2 = MinimalRulePostprocessor()

        result1 = p1.process("원문", "교정문1")
        result2 = p2.process("원문", "교정문2")

        assert isinstance(result1, str)
        assert isinstance(result2, str)

    def test_processor_is_stateless(self):
        """프로세서는 상태를 가지지 않음 (순수 함수)"""
        processor = MinimalRulePostprocessor()

        # 같은 입력은 항상 같은 출력
        result1 = processor.process("원문", "교정문")
        result2 = processor.process("원문", "교정문")
        result3 = processor.process("원문", "교정문")

        assert result1 == result2 == result3
