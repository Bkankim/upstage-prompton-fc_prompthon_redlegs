"""
문법 규칙 효과 정량화
"""
import pandas as pd

# 비교 파일 로드
comparison = pd.read_csv('outputs/version_comparison.csv')

print(f"=== 문법 규칙 효과 분석 ===\n")
print(f"총 차이 케이스: {len(comparison)}개 / 110개 ({len(comparison)/110*100:.1f}%)\n")

# 패턴별 분류
pattern_analysis = {
    "받아 봐": 0,  # 보조용언 띄어쓰기
    " 수 ": 0,      # 의존명사 띄어쓰기
    "돼": 0,        # 되/돼 변환
    "안 돼": 0,     # 안 돼 띄어쓰기
    "기타": 0
}

for _, row in comparison.iterrows():
    old = row['old_correction']
    new = row['new_correction']

    # 패턴 감지
    if ' 봐' in old and '봐' in new and ' 봐' not in new:
        pattern_analysis["받아 봐"] += 1
    elif ' 수 ' in old and ' 수 ' not in new:
        pattern_analysis[" 수 "] += 1
    elif '돼' in old and '되' in new:
        pattern_analysis["돼"] += 1
    elif '안 돼' in old and '안돼' in new:
        pattern_analysis["안 돼"] += 1
    else:
        pattern_analysis["기타"] += 1

print("=== 문법 규칙별 적용 횟수 ===")
for pattern, count in pattern_analysis.items():
    print(f"{pattern:10s}: {count:3d}회 ({count/len(comparison)*100:5.1f}%)")

# 심각한 오류 케이스 분석
serious_errors = []
for _, row in comparison.iterrows():
    old_len = len(row['old_correction'])
    new_len = len(row['new_correction'])

    # 길이가 50% 이상 차이나면 심각한 오류
    if abs(old_len - new_len) / old_len > 0.5:
        serious_errors.append({
            'id': row['id'],
            'old_len': old_len,
            'new_len': new_len,
            'diff': abs(old_len - new_len),
            'old': row['old_correction'][:100],
            'new': row['new_correction'][:100]
        })

print(f"\n=== 심각한 오류 케이스 ===")
print(f"총 {len(serious_errors)}개\n")

for err in serious_errors[:5]:
    print(f"ID: {err['id']}")
    print(f"길이 변화: {err['old_len']} → {err['new_len']} ({err['diff']}자 차이)")
    print(f"이전: {err['old']}...")
    print(f"현재: {err['new']}...")
    print()

# 결론
print("=== 결론 ===")
print(f"1. 문법 규칙은 {len(comparison)}개 케이스에 영향 ({len(comparison)/110*100:.1f}%)")
print(f"2. 심각한 오류(콜론 오작동): {len(serious_errors)}개")
print(f"3. 유용한 띄어쓰기 교정: ~{pattern_analysis['받아 봐'] + pattern_analysis[' 수 ']}개")
print(f"\n→ 문법 규칙은 유용하지만, 콜론 로직 개선 필수!")
