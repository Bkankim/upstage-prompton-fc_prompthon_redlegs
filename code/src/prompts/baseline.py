"""
베이스라인 프롬프트 클래스
"""

from .base import BasePrompt


class BaselinePrompt(BasePrompt):
    """
    기본 베이스라인 프롬프트
    단순하고 직접적인 교정 지시를 사용
    """

    @property
    def name(self) -> str:
        """프롬프트 이름 반환"""
        return "baseline"

    def system_message(self) -> str:
        """시스템 메시지 반환 (사용하지 않음)"""
        return ""

    def format_user_message(self, text: str) -> str:
        """
        사용자 메시지 포맷팅

        Args:
            text: 교정할 원문 텍스트

        Returns:
            str: 포맷팅된 프롬프트
        """
        template = """# 지시
- 다음 규칙에 따라 원문을 교정하세요.
- 맞춤법, 띄어쓰기, 문장 부호, 문법을 자연스럽게 교정합니다.
- 어떤 경우에도 설명이나 부가적인 내용은 포함하지 않습니다.
- 오직 교정된 문장만 출력합니다.

# 예시
<원문>
오늘 날씨가 않좋은데, 김치찌게 먹으러 갈려고.
<교정>
오늘 날씨가 안 좋은데, 김치찌개 먹으러 가려고.

# 교정할 문장
<원문>
{text}
<교정>"""

        return template.format(text=text)
