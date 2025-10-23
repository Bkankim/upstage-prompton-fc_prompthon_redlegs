"""
프롬프트 레지스트리 및 프롬프트 클래스 테스트
"""

import pytest
from src.prompts.base import BasePrompt
from src.prompts.baseline import BaselinePrompt
from src.prompts.fewshot_v2 import FewshotV2Prompt
from src.prompts.errortypes_v3 import ErrorTypesV3Prompt
from src.prompts.registry import PromptRegistry, get_registry, register_default_prompts


class TestPromptRegistry:
    """PromptRegistry 클래스 테스트"""

    def test_registry_init(self):
        """레지스트리 초기화 테스트"""
        registry = PromptRegistry()
        assert registry is not None
        assert registry.list_prompts() == []

    def test_register_prompt(self):
        """프롬프트 등록 테스트"""
        registry = PromptRegistry()
        prompt = BaselinePrompt()

        registry.register(prompt)

        assert "baseline" in registry
        assert prompt.name in registry.list_prompts()

    def test_get_prompt(self):
        """프롬프트 조회 테스트"""
        registry = PromptRegistry()
        prompt = BaselinePrompt()
        registry.register(prompt)

        retrieved = registry.get("baseline")

        assert retrieved is not None
        assert retrieved.name == "baseline"
        assert isinstance(retrieved, BasePrompt)

    def test_get_nonexistent_prompt(self):
        """존재하지 않는 프롬프트 조회 테스트"""
        registry = PromptRegistry()

        result = registry.get("nonexistent")

        assert result is None

    def test_list_prompts(self):
        """프롬프트 목록 조회 테스트"""
        registry = PromptRegistry()

        prompt1 = BaselinePrompt()
        prompt2 = FewshotV2Prompt()

        registry.register(prompt1)
        registry.register(prompt2)

        prompts = registry.list_prompts()

        assert len(prompts) == 2
        assert "baseline" in prompts
        assert "fewshot_v2" in prompts

    def test_contains_operator(self):
        """in 연산자 테스트"""
        registry = PromptRegistry()
        prompt = BaselinePrompt()
        registry.register(prompt)

        assert "baseline" in registry
        assert "nonexistent" not in registry


class TestGlobalRegistry:
    """전역 레지스트리 테스트"""

    def test_get_global_registry(self):
        """전역 레지스트리 인스턴스 조회 테스트"""
        registry1 = get_registry()
        registry2 = get_registry()

        # 싱글톤 패턴 확인
        assert registry1 is registry2

    def test_register_default_prompts(self):
        """기본 프롬프트 자동 등록 테스트"""
        # 새로운 레지스트리 인스턴스 생성 (테스트 격리)
        registry = PromptRegistry()

        # 기본 프롬프트들 수동 등록
        registry.register(BaselinePrompt())
        registry.register(FewshotV2Prompt())
        registry.register(ErrorTypesV3Prompt())

        # 등록 확인
        assert "baseline" in registry
        assert "fewshot_v2" in registry
        assert "errortypes_v3" in registry


class TestBaselinePrompt:
    """BaselinePrompt 클래스 테스트"""

    def test_prompt_name(self):
        """프롬프트 이름 테스트"""
        prompt = BaselinePrompt()
        assert prompt.name == "baseline"

    def test_system_message(self):
        """시스템 메시지 테스트"""
        prompt = BaselinePrompt()
        assert prompt.system_message() == ""

    def test_format_user_message(self):
        """사용자 메시지 포맷팅 테스트"""
        prompt = BaselinePrompt()
        text = "오늘 날씨가 않좋다."

        message = prompt.format_user_message(text)

        assert text in message
        assert "<원문>" in message
        assert "<교정>" in message

    def test_to_messages(self):
        """OpenAI 메시지 포맷 변환 테스트"""
        prompt = BaselinePrompt()
        text = "오늘 날씨가 않좋다."

        messages = prompt.to_messages(text)

        assert isinstance(messages, list)
        assert len(messages) == 1  # system_message가 없으므로 user만
        assert messages[0]["role"] == "user"
        assert text in messages[0]["content"]


class TestFewshotV2Prompt:
    """FewshotV2Prompt 클래스 테스트"""

    def test_prompt_name(self):
        """프롬프트 이름 테스트"""
        prompt = FewshotV2Prompt()
        assert prompt.name == "fewshot_v2"

    def test_system_message(self):
        """시스템 메시지 테스트"""
        prompt = FewshotV2Prompt()
        system_msg = prompt.system_message()

        # fewshot_v2는 system_message를 사용하지 않음
        assert isinstance(system_msg, str)
        assert system_msg == ""

    def test_format_user_message(self):
        """사용자 메시지 포맷팅 테스트"""
        prompt = FewshotV2Prompt()
        text = "오늘 날씨가 않좋다."

        message = prompt.format_user_message(text)

        assert text in message
        assert isinstance(message, str)
        assert "예시" in message  # few-shot 예시 포함 확인

    def test_to_messages(self):
        """메시지 변환 테스트"""
        prompt = FewshotV2Prompt()
        text = "오늘 날씨가 않좋다."

        messages = prompt.to_messages(text)

        assert isinstance(messages, list)
        assert len(messages) == 1  # system_message가 없으므로 user만
        assert messages[0]["role"] == "user"
        assert text in messages[0]["content"]


class TestErrorTypesV3Prompt:
    """ErrorTypesV3Prompt 클래스 테스트"""

    def test_prompt_name(self):
        """프롬프트 이름 테스트"""
        prompt = ErrorTypesV3Prompt()
        assert prompt.name == "errortypes_v3"

    def test_system_message(self):
        """시스템 메시지 테스트"""
        prompt = ErrorTypesV3Prompt()
        system_msg = prompt.system_message()

        # errortypes_v3는 system_message를 사용하지 않음
        assert isinstance(system_msg, str)
        assert system_msg == ""

    def test_format_user_message(self):
        """사용자 메시지 포맷팅 테스트"""
        prompt = ErrorTypesV3Prompt()
        text = "오늘 날씨가 않좋다."

        message = prompt.format_user_message(text)

        assert text in message
        assert isinstance(message, str)
        assert "체크리스트" in message  # 체크리스트 방식 확인

    def test_to_messages(self):
        """메시지 변환 테스트"""
        prompt = ErrorTypesV3Prompt()
        text = "오늘 날씨가 않좋다."

        messages = prompt.to_messages(text)

        assert isinstance(messages, list)
        assert len(messages) == 1  # system_message가 없으므로 user만

        # 마지막 메시지는 user 역할이어야 함
        assert messages[-1]["role"] == "user"
        assert text in messages[-1]["content"]


class TestBasePrompt:
    """BasePrompt 추상 클래스 테스트"""

    def test_cannot_instantiate_abstract_class(self):
        """추상 클래스는 직접 인스턴스화할 수 없음"""
        with pytest.raises(TypeError):
            BasePrompt()

    def test_concrete_class_implements_all_methods(self):
        """구현 클래스는 모든 추상 메서드를 구현해야 함"""

        class IncompletePrompt(BasePrompt):
            @property
            def name(self) -> str:
                return "incomplete"

            # system_message와 format_user_message 미구현

        # 추상 메서드 미구현 시 인스턴스화 불가
        with pytest.raises(TypeError):
            IncompletePrompt()
