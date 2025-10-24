"""
Baseline + 띄어쓰기 예시 1개

전략:
- Baseline의 맞춤법 예시를 띄어쓰기 예시로 변경
- 1개 예시가 최적점 (34.04%)이므로 예시 내용만 변경
- 띄어쓰기는 가장 일반적이고 중요한 오류 유형
"""

from .base import BasePrompt


class BaselineSpacingPrompt(BasePrompt):
    """
    Baseline + 띄어쓰기 예시 1개

    특징:
    - 1개 예시 사용 (Baseline과 동일 구조)
    - 띄어쓰기 오류에 집중
    - 목표: 34%+ 달성
    """

    @property
    def name(self) -> str:
        return "baseline_spacing"

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
그는 삼성전자의 제안을 받아봤지만 탐탁치않게 여겼다.
<교정>
그는 삼성전자의 제안을 받아 봤지만 탐탁지 않게 여겼다.

# 교정할 문장
<원문>
{text}
<교정>"""

        return template.format(text=text)
