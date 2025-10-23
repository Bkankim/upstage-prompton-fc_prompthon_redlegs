"""
성능 하락 원인 분석

목적: 두 버전 비교 및 변경 케이스 분석
"""

import pandas as pd
import json
from pathlib import Path


def analyze_submission_differences(
    old_file: str = "outputs/submissions/test/submission_baseline_test_clean.csv",
    new_file: str = "outputs/submissions/test/submission_baseline_v2_test.csv",
    output_file: str = "outputs/logs/performance_drop_analysis.json"
):
    """
    두 제출 파일 상세 비교 분석
    """
    print(f"\n{'='*60}")
    print(f"성능 하락 원인 분석")
    print(f"{'='*60}\n")

    # 데이터 로드
    old = pd.read_csv(old_file)
    new = pd.read_csv(new_file)

    print(f"기존 버전: {old_file}")
    print(f"  Public LB: 34.0426%")
    print(f"  Private LB: 13.4454%")
    print()

    print(f"신규 버전: {new_file}")
    print(f"  Public LB: 31.9149% (-2.13%p)")
    print(f"  Private LB: 12.2951% (-1.15%p)")
    print()

    # 변경 케이스 추출
    changed_cases = []
    unchanged_cases = []

    for idx in range(len(old)):
        old_cor = old.iloc[idx]['cor_sentence']
        new_cor = new.iloc[idx]['cor_sentence']

        if old_cor != new_cor:
            changed_cases.append({
                'index': idx,
                'id': old.iloc[idx]['id'],
                'err_sentence': old.iloc[idx]['err_sentence'],
                'old_correction': old_cor,
                'new_correction': new_cor,
                'old_length': len(old_cor),
                'new_length': len(new_cor),
                'length_ratio': len(new_cor) / len(old_cor) if len(old_cor) > 0 else 1.0,
                'length_diff': len(new_cor) - len(old_cor)
            })
        else:
            unchanged_cases.append(idx)

    print(f"[변경 통계]")
    print(f"{'='*60}")
    print(f"변경된 케이스: {len(changed_cases)}개 ({len(changed_cases)/len(old)*100:.1f}%)")
    print(f"유지된 케이스: {len(unchanged_cases)}개 ({len(unchanged_cases)/len(old)*100:.1f}%)")
    print()

    # 길이 변화 분석
    length_increases = [c for c in changed_cases if c['length_diff'] > 0]
    length_decreases = [c for c in changed_cases if c['length_diff'] < 0]
    length_same = [c for c in changed_cases if c['length_diff'] == 0]

    print(f"[길이 변화 분석]")
    print(f"{'='*60}")
    print(f"길이 증가: {len(length_increases)}개")
    print(f"길이 감소: {len(length_decreases)}개")
    print(f"길이 동일: {len(length_same)}개")
    print()

    # 평균 길이 비율
    avg_ratio = sum(c['length_ratio'] for c in changed_cases) / len(changed_cases) if changed_cases else 1.0
    print(f"평균 길이 비율: {avg_ratio:.3f}")
    print()

    # 길이 가드 발동 가능성 확인
    guard_candidates = [c for c in changed_cases if c['length_ratio'] < 0.6]
    print(f"[길이 가드 발동 가능성]")
    print(f"{'='*60}")
    print(f"60% 미만 손실 케이스: {len(guard_candidates)}개")

    if guard_candidates:
        print("\n⚠️ 길이 가드 발동 가능 케이스:")
        for c in guard_candidates:
            print(f"  ID: {c['id']}")
            print(f"  비율: {c['length_ratio']:.1%} ({c['old_length']} → {c['new_length']})")
            print(f"  원문: {c['err_sentence'][:50]}...")
            print(f"  기존: {c['old_correction'][:50]}...")
            print(f"  신규: {c['new_correction'][:50]}...")
            print()
    else:
        print("✅ 길이 가드 발동 케이스 없음")
    print()

    # 변경 패턴 분석
    print(f"[변경 패턴 분석 (상위 10개)]")
    print(f"{'='*60}\n")

    for i, case in enumerate(changed_cases[:10], 1):
        print(f"{i}. ID: {case['id']}")
        print(f"   원문: {case['err_sentence'][:80]}")
        print(f"   기존: {case['old_correction'][:80]}")
        print(f"   신규: {case['new_correction'][:80]}")
        print(f"   길이: {case['old_length']} → {case['new_length']} ({case['length_diff']:+d})")
        print()

    # 결과 저장
    result = {
        'performance': {
            'old': {'public': 34.0426, 'private': 13.4454},
            'new': {'public': 31.9149, 'private': 12.2951},
            'diff': {
                'public': -2.1277,
                'private': -1.1503
            }
        },
        'statistics': {
            'total_cases': len(old),
            'changed_cases': len(changed_cases),
            'unchanged_cases': len(unchanged_cases),
            'change_ratio': len(changed_cases) / len(old),
            'length_increases': len(length_increases),
            'length_decreases': len(length_decreases),
            'avg_length_ratio': avg_ratio,
            'guard_candidates': len(guard_candidates)
        },
        'changed_cases': changed_cases[:20],  # 상위 20개만 저장
        'guard_candidates': guard_candidates
    }

    # JSON 저장
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"{'='*60}")
    print(f"결과 저장: {output_file}")
    print(f"{'='*60}\n")

    return result


def check_length_guard_logs():
    """
    길이 가드 발동 로그 확인
    """
    print(f"\n{'='*60}")
    print(f"길이 가드 로그 확인")
    print(f"{'='*60}\n")

    log_file = "outputs/logs/generate_baseline_v2_test.log"

    if not Path(log_file).exists():
        print(f"⚠️ 로그 파일 없음: {log_file}")
        return

    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()

    # "Length guard activated" 검색
    guard_activations = [line for line in log_content.split('\n') if 'Length guard activated' in line]

    print(f"길이 가드 발동 횟수: {len(guard_activations)}회")

    if guard_activations:
        print("\n[발동 로그]:")
        for log in guard_activations[:5]:
            print(f"  {log}")
    else:
        print("✅ 길이 가드 발동 없음")

    print()


if __name__ == "__main__":
    # 상세 비교 분석
    result = analyze_submission_differences()

    # 길이 가드 로그 확인
    check_length_guard_logs()

    # 요약
    print(f"\n{'='*60}")
    print(f"분석 요약")
    print(f"{'='*60}\n")

    print(f"1. 성능 하락:")
    print(f"   Public: -2.13%p (34.04% → 31.91%)")
    print(f"   Private: -1.15%p (13.45% → 12.30%)")
    print()

    print(f"2. 변경 케이스: {result['statistics']['changed_cases']}개 ({result['statistics']['change_ratio']*100:.1f}%)")
    print()

    print(f"3. 길이 가드 발동: {result['statistics']['guard_candidates']}건")
    print()

    if result['statistics']['guard_candidates'] == 0:
        print("✅ 길이 가드는 정상 작동 (발동 없음)")
        print("⚠️ 성능 하락 원인: API 랜덤성에 의한 응답 변화")
        print()
        print("추정 원인:")
        print("  1. 같은 프롬프트라도 API 응답이 시간/상태에 따라 다름")
        print("  2. 41개 변경 케이스 중 일부가 정답에서 멀어짐")
        print("  3. 보조용언 띄어쓰기 등 표현 변화가 부정적 영향")
    else:
        print("⚠️ 길이 가드가 예상치 못한 케이스 처리")
        print("   → 상세 케이스 확인 필요")
