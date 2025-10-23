"""
프롬프트 기본 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BasePrompt(ABC):
    """
    모든 프롬프트 클래스의 기본 추상 클래스
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        프롬프트의 고유 이름 반환

        Returns:
            str: 프롬프트 이름
        """
        pass

    @abstractmethod
    def system_message(self) -> str:
        """
        시스템 메시지 반환

        Returns:
            str: 시스템 프롬프트 내용
        """
        pass

    @abstractmethod
    def format_user_message(self, text: str) -> str:
        """
        사용자 메시지 포맷팅

        Args:
            text: 교정할 원문 텍스트

        Returns:
            str: 포맷팅된 사용자 메시지
        """
        pass

    def to_messages(self, text: str) -> List[Dict[str, Any]]:
        """
        OpenAI API 포맷으로 메시지 변환

        Args:
            text: 교정할 원문 텍스트

        Returns:
            List[Dict[str, Any]]: OpenAI API 메시지 포맷
        """
        messages = []

        system_msg = self.system_message()
        if system_msg:
            messages.append({
                "role": "system",
                "content": system_msg
            })

        messages.append({
            "role": "user",
            "content": self.format_user_message(text)
        })

        return messages
