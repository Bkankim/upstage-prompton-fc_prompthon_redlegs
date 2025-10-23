"""
후처리 기본 추상 클래스
"""

from abc import ABC, abstractmethod


class BasePostprocessor(ABC):
    """
    후처리 클래스의 기본 추상 클래스
    모든 후처리 클래스는 이 클래스를 상속받아 구현해야 함
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        후처리 모듈의 이름을 반환

        Returns:
            str: 후처리 모듈 이름
        """
        pass

    @abstractmethod
    def process(self, original: str, corrected: str) -> str:
        """
        원문과 교정문을 받아서 후처리 수행

        Args:
            original: 원문 텍스트
            corrected: 교정된 텍스트

        Returns:
            str: 후처리된 텍스트 (실패 시 원문 반환)
        """
        pass
