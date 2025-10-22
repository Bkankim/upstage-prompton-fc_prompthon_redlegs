"""
프롬프트 모듈 사용 예시
"""

from src.prompts import get_registry


def example_basic_usage():
    """기본 사용법 예시"""
    print("=" * 60)
    print("기본 사용법")
    print("=" * 60)

    # 레지스트리에서 프롬프트 가져오기
    registry = get_registry()

    # 사용 가능한 프롬프트 확인
    print(f"사용 가능한 프롬프트: {registry.list_prompts()}")
    print()

    # 특정 프롬프트 사용
    test_text = "오늘 날씨가 않좋아."

    baseline = registry.get("baseline")
    user_message = baseline.format_user_message(test_text)

    print("Baseline 프롬프트 결과:")
    print("-" * 60)
    print(user_message)
    print()


def example_api_format():
    """API 포맷 변환 예시"""
    print("=" * 60)
    print("OpenAI API 포맷 변환")
    print("=" * 60)

    registry = get_registry()
    test_text = "오늘 날씨가 않좋아."

    # to_messages() 메서드로 API 포맷 변환
    baseline = registry.get("baseline")
    messages = baseline.to_messages(test_text)

    print(f"메시지 개수: {len(messages)}")
    for i, msg in enumerate(messages, 1):
        print(f"\n메시지 {i}:")
        print(f"  - role: {msg['role']}")
        print(f"  - content 길이: {len(msg['content'])} 자")
    print()


def example_compare_prompts():
    """여러 프롬프트 비교 예시"""
    print("=" * 60)
    print("프롬프트 비교")
    print("=" * 60)

    registry = get_registry()
    test_text = "오늘 날씨가 않좋아."

    for name in registry.list_prompts():
        prompt = registry.get(name)
        user_message = prompt.format_user_message(test_text)
        message_length = len(user_message)

        print(f"\n{name} 프롬프트:")
        print(f"  - 메시지 길이: {message_length} 자")
        print(f"  - 예시 개수: {user_message.count('# 예시')} 개")
        print(f"  - 첫 50자: {user_message[:50]}...")


def main():
    """메인 실행"""
    print("\n프롬프트 모듈 사용 예시\n")

    example_basic_usage()
    example_api_format()
    example_compare_prompts()

    print("=" * 60)
    print("예시 종료")
    print("=" * 60)


if __name__ == "__main__":
    main()
