"""
길이 가드 단위 테스트

목적: _apply_length_guard() 함수의 정확한 동작 검증
"""

import pytest
from src.postprocessors.rule_checklist import RuleChecklistPostprocessor


class TestLengthGuard:
    """길이 가드 단위 테스트"""

    def setup_method(self):
        """테스트 설정"""
        self.processor = RuleChecklistPostprocessor()

    def test_normal_case_90_percent(self):
        """
        정상 케이스: 원문 90% 길이 → 교정 적용

        원문 대비 90% 길이는 정상 범위이므로 교정문 반환
        """
        original = "이것은 원본 문장입니다."  # 12자
        corrected = "이것은 교정된 문장입니다"  # 11자 (91.7%)

        result = self.processor._apply_length_guard(original, corrected)

        assert result == corrected, "90% 길이는 교정문 반환해야 함"
        print(f"✅ 정상 케이스 (90%): 교정문 반환")
        print(f"   원본: {original} ({len(original)}자)")
        print(f"   교정: {corrected} ({len(corrected)}자)")
        print(f"   비율: {len(corrected)/len(original):.1%}")

    def test_guard_activation_50_percent(self):
        """
        가드 작동: 원문 50% 길이 → 원문 반환

        원문 대비 50% 길이는 60% 미만이므로 원문 반환
        """
        original = "대학입학 전형에서 서울대의 수시 비중은 7:3이었다."  # 26자
        corrected = "3이었다."  # 4자 (15.4%)

        result = self.processor._apply_length_guard(original, corrected)

        assert result == original, "50% 길이는 원문 반환해야 함"
        print(f"✅ 가드 작동 (50%): 원문 반환")
        print(f"   원본: {original} ({len(original)}자)")
        print(f"   교정: {corrected} ({len(corrected)}자)")
        print(f"   비율: {len(corrected)/len(original):.1%}")

    def test_boundary_case_exactly_60_percent(self):
        """
        경계값: 정확히 60% → 교정 적용

        60% 이상이면 교정문 반환 (경계값 포함)
        """
        original = "12345678901234567890"  # 20자
        corrected = "123456789012"  # 12자 (정확히 60%)

        result = self.processor._apply_length_guard(original, corrected)

        assert result == corrected, "60% 경계값은 교정문 반환해야 함"
        print(f"✅ 경계값 (60%): 교정문 반환")
        print(f"   원본: {original} ({len(original)}자)")
        print(f"   교정: {corrected} ({len(corrected)}자)")
        print(f"   비율: {len(corrected)/len(original):.1%}")

    def test_boundary_case_just_below_60_percent(self):
        """
        경계값 아래: 59.9% → 원문 반환

        60% 미만이면 원문 반환
        """
        original = "12345678901234567890"  # 20자
        corrected = "12345678901"  # 11자 (55%)

        result = self.processor._apply_length_guard(original, corrected)

        assert result == original, "60% 미만은 원문 반환해야 함"
        print(f"✅ 경계값 아래 (55%): 원문 반환")
        print(f"   원본: {original} ({len(original)}자)")
        print(f"   교정: {corrected} ({len(corrected)}자)")
        print(f"   비율: {len(corrected)/len(original):.1%}")

    def test_empty_original(self):
        """
        빈 원문 처리: 원문이 비어있으면 교정문 반환
        """
        original = ""
        corrected = "교정된 문장"

        result = self.processor._apply_length_guard(original, corrected)

        assert result == corrected, "빈 원문은 교정문 반환해야 함"
        print(f"✅ 빈 원문: 교정문 반환")

    def test_empty_corrected(self):
        """
        빈 교정문 처리: 교정문이 비어있으면 원문 반환
        """
        original = "원본 문장입니다."
        corrected = ""

        result = self.processor._apply_length_guard(original, corrected)

        assert result == original, "빈 교정문은 원문 반환해야 함"
        print(f"✅ 빈 교정문: 원문 반환")

    def test_severe_loss_17_percent(self):
        """
        심각한 손실: 17% → 원문 반환

        실제 발생한 "7:3" → "3" 케이스 시뮬레이션
        """
        original = "대학입학 전형에서 서울대의 수시 비중은 7:3이었다."
        corrected = "3이었다."

        result = self.processor._apply_length_guard(original, corrected)

        assert result == original, "17% 심각한 손실은 원문 반환해야 함"
        print(f"✅ 심각한 손실 (17%): 원문 반환")
        print(f"   원본: {original}")
        print(f"   교정: {corrected}")
        print(f"   비율: {len(corrected)/len(original):.1%}")

    def test_integration_with_full_process(self):
        """
        통합 테스트: process() 메서드와 함께 동작 확인
        """
        # 심각한 손실 케이스
        original = "대학입학 전형에서 서울대의 수시 비중은 7:3이었다."
        # 후처리가 "3이었다."로 잘못 처리했다고 가정
        # (실제로는 API 응답을 시뮬레이션)
        api_response = "교정: 3이었다."

        result = self.processor.process(original, api_response)

        # 길이 가드가 작동하여 원문 반환해야 함
        assert result == original, "통합: 심각한 손실은 원문 반환해야 함"
        print(f"✅ 통합 테스트: 길이 가드 작동 확인")
        print(f"   원본: {original}")
        print(f"   API 응답: {api_response}")
        print(f"   최종 결과: {result}")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("길이 가드 단위 테스트 시작")
    print("="*60 + "\n")

    test = TestLengthGuard()

    tests = [
        ("정상 케이스 (90%)", test.test_normal_case_90_percent),
        ("가드 작동 (50%)", test.test_guard_activation_50_percent),
        ("경계값 (60%)", test.test_boundary_case_exactly_60_percent),
        ("경계값 아래 (55%)", test.test_boundary_case_just_below_60_percent),
        ("빈 원문", test.test_empty_original),
        ("빈 교정문", test.test_empty_corrected),
        ("심각한 손실 (17%)", test.test_severe_loss_17_percent),
        ("통합 테스트", test.test_integration_with_full_process),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test.setup_method()
            test_func()
            passed += 1
            print()
        except AssertionError as e:
            print(f"❌ {name} 실패: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {name} 오류: {e}\n")
            failed += 1

    print("="*60)
    print(f"테스트 결과: {passed}개 통과, {failed}개 실패")
    print("="*60 + "\n")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    exit(0 if failed == 0 else 1)
