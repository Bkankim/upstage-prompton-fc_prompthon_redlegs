"""
Baseline + Few-shot 3개 예시 프롬프트

목표:
- Baseline의 단순함 유지
- 약점 유형만 타겟팅 (조사, 사이시옷, 표현다듬기)
- 과적합 방지 (3개 예시만)
"""

from .base import BasePrompt


class BaselinePlus3ExamplesPrompt(BasePrompt):
    """
    Baseline + 약점 유형 3개 예시 추가

    보수적 개선 전략:
    - 기존 Baseline 구조 유지
    - 조사오류, 사이시옷, 표현다듬기 예시만 추가
    - 최소한의 변화로 최대 효과
    """

    @property
    def name(self) -> str:
        """프롬프트 이름 반환"""
        return "baseline_plus_3examples"

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

## 맞춤법
<원문>
오늘 날씨가 않좋은데, 김치찌게 먹으러 갈려고.
<교정>
오늘 날씨가 안 좋은데, 김치찌개 먹으러 가려고.

## 조사 오류
<원문>
그는 삼성전자의 제안을 탐탁치 않게 여겼다.
<교정>
그는 삼성전자의 제안을 탐탁지 않게 여겼다.

## 사이시옷
<원문>
그녀는 개나리꽃길을 따라 천천히 걸어갔다.
<교정>
그녀는 개나리꽃 길을 따라 천천히 걸어갔다.

## 표현 다듬기
<원문>
이 제품은 정말 최고의 성능을 발휘하는 아주 좋은 제품입니다.
<교정>
이 제품은 최고의 성능을 발휘하는 좋은 제품입니다.

# 교정할 문장
<원문>
{text}
<교정>"""

        return template.format(text=text)
