"""
프롬프트 모듈 검증 스크립트
"""

from src.prompts import get_registry, BaselinePrompt, FewshotV2Prompt, ErrorTypesV3Prompt
import prompts


def test_registry():
    """레지스트리 기능 검증"""
    print("=" * 60)
    print("1. 레지스트리 검증")
    print("=" * 60)

    registry = get_registry()

    # 프롬프트 목록 확인
    prompt_list = registry.list_prompts()
    print(f"등록된 프롬프트 목록: {prompt_list}")

    expected_prompts = ['baseline', 'fewshot_v2', 'errortypes_v3']
    assert set(prompt_list) == set(expected_prompts), f"예상: {expected_prompts}, 실제: {prompt_list}"
    print("✓ 프롬프트 목록 확인 성공")

    # 각 프롬프트 조회 확인
    for name in expected_prompts:
        prompt = registry.get(name)
        assert prompt is not None, f"{name} 프롬프트를 찾을 수 없음"
        print(f"✓ {name} 프롬프트 조회 성공")

    print()


def test_prompt_format():
    """프롬프트 포맷팅 검증"""
    print("=" * 60)
    print("2. 프롬프트 포맷팅 검증")
    print("=" * 60)

    test_text = "오늘 날씨가 않좋아."

    registry = get_registry()

    # Baseline 프롬프트 테스트
    baseline = registry.get("baseline")
    baseline_msg = baseline.format_user_message(test_text)
    assert test_text in baseline_msg, "원문 텍스트가 포맷팅된 메시지에 포함되지 않음"
    assert "<원문>" in baseline_msg, "원문 태그가 없음"
    assert "<교정>" in baseline_msg, "교정 태그가 없음"
    print("✓ Baseline 프롬프트 포맷팅 성공")

    # to_messages() 메서드 테스트
    messages = baseline.to_messages(test_text)
    assert len(messages) >= 1, "메시지가 생성되지 않음"
    assert messages[-1]["role"] == "user", "마지막 메시지가 user 역할이 아님"
    print("✓ to_messages() 메서드 동작 성공")

    print()


def test_backward_compatibility():
    """기존 prompts.py와의 호환성 검증"""
    print("=" * 60)
    print("3. 기존 prompts.py 호환성 검증")
    print("=" * 60)

    # 기존 프롬프트 변수들이 존재하는지 확인
    assert hasattr(prompts, 'baseline_prompt'), "baseline_prompt가 없음"
    assert hasattr(prompts, 'fewshot_v2_prompt'), "fewshot_v2_prompt가 없음"
    assert hasattr(prompts, 'errortypes_v3_prompt'), "errortypes_v3_prompt가 없음"
    print("✓ 기존 prompts.py의 변수들이 모두 존재함")

    # 기존 프롬프트 내용 확인
    test_text = "테스트 문장"

    old_baseline = prompts.baseline_prompt.format(text=test_text)
    new_baseline = get_registry().get("baseline").format_user_message(test_text)
    assert old_baseline == new_baseline, "Baseline 프롬프트 내용이 다름"
    print("✓ Baseline 프롬프트 내용 일치")

    old_fewshot = prompts.fewshot_v2_prompt.format(text=test_text)
    new_fewshot = get_registry().get("fewshot_v2").format_user_message(test_text)
    assert old_fewshot == new_fewshot, "Fewshot v2 프롬프트 내용이 다름"
    print("✓ Fewshot v2 프롬프트 내용 일치")

    old_errortypes = prompts.errortypes_v3_prompt.format(text=test_text)
    new_errortypes = get_registry().get("errortypes_v3").format_user_message(test_text)
    assert old_errortypes == new_errortypes, "Error Types v3 프롬프트 내용이 다름"
    print("✓ Error Types v3 프롬프트 내용 일치")

    print()


def main():
    """메인 검증 실행"""
    print("\n프롬프트 모듈 검증 시작\n")

    try:
        test_registry()
        test_prompt_format()
        test_backward_compatibility()

        print("=" * 60)
        print("모든 검증 통과")
        print("=" * 60)
        print("\n요약:")
        print("- 레지스트리 기능: 정상")
        print("- 프롬프트 포맷팅: 정상")
        print("- 기존 코드 호환성: 정상")
        print("\n사용 가능한 프롬프트: baseline, fewshot_v2, errortypes_v3")

    except AssertionError as e:
        print(f"\n❌ 검증 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
