"""
두 버전의 제출 파일 비교 분석
"""
import pandas as pd

# 파일 로드
old_file = "outputs/submissions/test/submission_baseline_test_clean.csv"  # 문법 규칙 포함 (Public 34.04%)
new_file = "outputs/baseline_test.csv"  # Response Cleaning만 (Public 31.91%)

old_df = pd.read_csv(old_file)
new_df = pd.read_csv(new_file)

print(f"=== 파일 비교 ===")
print(f"이전 파일 (문법 규칙 포함): {old_file}")
print(f"현재 파일 (Response Cleaning만): {new_file}")
print(f"행 수: 이전={len(old_df)}, 현재={len(new_df)}")

# 차이가 있는 케이스 찾기
differences = []
for idx, row in old_df.iterrows():
    old_cor = row['cor_sentence']
    new_cor = new_df.loc[new_df['id'] == row['id'], 'cor_sentence'].values[0]

    if old_cor != new_cor:
        differences.append({
            'id': row['id'],
            'err_sentence': row['err_sentence'],
            'old_correction': old_cor,
            'new_correction': new_cor
        })

print(f"\n=== 차이 분석 ===")
print(f"전체 케이스: {len(old_df)}개")
print(f"차이 발생: {len(differences)}개 ({len(differences)/len(old_df)*100:.1f}%)")

if len(differences) > 0:
    print(f"\n=== 차이 발생 케이스 상세 ===")
    for i, diff in enumerate(differences[:20], 1):  # 처음 20개만 출력
        print(f"\n[{i}] ID: {diff['id']}")
        print(f"원문: {diff['err_sentence'][:80]}...")
        print(f"이전 (문법 규칙 포함): {diff['old_correction'][:100]}...")
        print(f"현재 (Cleaning만):     {diff['new_correction'][:100]}...")

        # 차이 분석
        old = diff['old_correction']
        new = diff['new_correction']

        # 패턴 분석
        patterns_found = []
        if '돼' in old and '되' in new:
            patterns_found.append("되/돼 변환")
        if ' 수 ' in old and '수' in new:
            patterns_found.append("의존명사 띄어쓰기")
        if ' 보' in old and '보' in new:
            patterns_found.append("보조용언 띄어쓰기")
        if '안 돼' in old and '안돼' in new:
            patterns_found.append("안 돼 띄어쓰기")

        if patterns_found:
            print(f"패턴: {', '.join(patterns_found)}")

    # 전체 차이 저장
    diff_df = pd.DataFrame(differences)
    diff_df.to_csv('outputs/version_comparison.csv', index=False)
    print(f"\n전체 차이 케이스 저장: outputs/version_comparison.csv")
