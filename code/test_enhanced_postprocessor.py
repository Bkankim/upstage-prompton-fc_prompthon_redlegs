"""
Enhanced 후처리 모듈 단위 테스트 및 드라이런
"""

import json
from src.postprocessors.enhanced_postprocessor import EnhancedPostprocessor


def test_enhanced_postprocessor():
    """
    Enhanced 후처리 모듈 단위 테스트
    """
    print("="*70)
    print("Enhanced Postprocessor 단위 테스트")
    print("="*70)
    print()

    postprocessor = EnhancedPostprocessor(enable_logging=True)

    # 테스트 케이스 1: 메타데이터 제거
    print("Test 1: 메타데이터 제거")
    test_case_1 = {
        'original': '리조트 수요가 급증했다.',
        'corrected': '※ 원칙 준수: 리조트 수요가 급증했다. [최종 출력] 리조트 수요가 급증했다.'
    }
    result_1 = postprocessor.process(
        test_case_1['original'],
        test_case_1['corrected']
    )
    print(f"  원문   : {test_case_1['original']}")
    print(f"  입력   : {test_case_1['corrected']}")
    print(f"  출력   : {result_1}")
    print(f"  성공   : {'✅' if result_1 == test_case_1['original'] else '❌'}")
    print()

    # 테스트 케이스 2: 반복 문장 제거
    print("Test 2: 반복 문장 제거")
    test_case_2 = {
        'original': '그가 벽에 부딪혀 넘어졌다.',
        'corrected': '그가 벽에 부딪혀 넘어졌다. 그가 벽에 부딪혀 넘어졌다.'
    }
    result_2 = postprocessor.process(
        test_case_2['original'],
        test_case_2['corrected']
    )
    print(f"  원문   : {test_case_2['original']}")
    print(f"  입력   : {test_case_2['corrected']}")
    print(f"  출력   : {result_2}")
    print(f"  성공   : {'✅' if result_2 == test_case_2['original'] else '❌'}")
    print()

    # 테스트 케이스 3: 숫자/단위 복원
    print("Test 3: 숫자/단위 복원")
    test_case_3 = {
        'original': '관광객은 누적 186만명으로, 작년 대비 31% 늘어났다.',
        'corrected': '관광객은 누적 186만 명으로, 작년 대비 31% 늘어났다.'
    }
    result_3 = postprocessor.process(
        test_case_3['original'],
        test_case_3['corrected']
    )
    print(f"  원문   : {test_case_3['original']}")
    print(f"  입력   : {test_case_3['corrected']}")
    print(f"  출력   : {result_3}")
    print(f"  변경됨 : {'186만 명' in test_case_3['corrected']}")
    print(f"  복원됨 : {'186만명' in result_3}")
    print()

    # 테스트 케이스 4: Index 123 패턴 (최악의 케이스)
    print("Test 4: Index 123 패턴 (메타데이터 폭발)")
    test_case_4 = {
        'original': '리조트 수요의 귀환은 관광객 급증이 결정적이었는 분석이다.',
        'corrected': '''수정 사항:다최종 교정 문장 (원칙 준수):원칙 적용 재확인:
최종 출력 (요구사항 충족):※ 참고:다최종 한 줄 출력 (원칙 3 준수):
오류 재확인:최종 답변:※ 추가 설명 생략 (원칙 3 준수):
리조트 수요의 귀환은 관광객 급증이 결정적이었는 분석이다.'''
    }
    result_4 = postprocessor.process(
        test_case_4['original'],
        test_case_4['corrected']
    )
    print(f"  원문   : {test_case_4['original']}")
    print(f"  입력   : {test_case_4['corrected'][:100]}... (총 {len(test_case_4['corrected'])}자)")
    print(f"  출력   : {result_4}")
    print(f"  메타데이터 제거됨: {'✅' if len(result_4) < 200 else '❌'}")
    print()

    # 요약 통계
    print("="*70)
    print("처리 로그 요약 통계")
    print("="*70)
    summary = postprocessor.get_processing_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print()

    # 로그 저장
    print("처리 로그 저장 중...")
    postprocessor.save_processing_log('outputs/analysis/postprocess_test_comparison.json')
    print("✅ 저장 완료: outputs/analysis/postprocess_test_comparison.json")


if __name__ == "__main__":
    test_enhanced_postprocessor()
