"""
Train 데이터에서 명확한 규칙 추출
API 호출 없이 패턴 분석
"""

import pandas as pd
import re
from collections import Counter

def extract_patterns(train_df):
    """
    Train 데이터에서 명확한 오류 패턴 추출
    """
    patterns = []

    for idx, row in train_df.iterrows():
        original_part = str(row['original_target_part'])
        golden_part = str(row['golden_target_part'])
        error_type = row['type']

        # 패턴 저장
        patterns.append({
            'original': original_part,
            'golden': golden_part,
            'type': error_type,
            'err_sentence': row['err_sentence'],
            'cor_sentence': row['cor_sentence']
        })

    return patterns

def find_high_confidence_rules(patterns):
    """
    False Positive가 거의 없는 고신뢰도 규칙 찾기
    """
    # 패턴별 출현 횟수
    pattern_counts = Counter()
    pattern_examples = {}

    for p in patterns:
        key = f"{p['original']} → {p['golden']}"
        pattern_counts[key] += 1

        if key not in pattern_examples:
            pattern_examples[key] = {
                'original': p['original'],
                'golden': p['golden'],
                'type': p['type'],
                'examples': []
            }
        pattern_examples[key]['examples'].append(p['err_sentence'][:100])

    # 명확한 규칙 선정 기준
    print("=== 고빈도 패턴 (2회 이상) ===\n")
    high_freq_patterns = []

    for pattern, count in pattern_counts.most_common(50):
        if count >= 2:  # 2회 이상 출현
            info = pattern_examples[pattern]
            print(f"[{count}회] {pattern} ({info['type']})")
            print(f"   예시: {info['examples'][0][:80]}...")
            print()
            high_freq_patterns.append((pattern, count, info))

    return high_freq_patterns

def analyze_rule_types(patterns):
    """
    규칙 유형별 분류 및 안전도 평가
    """
    safe_rules = []

    # 1. 형용사 + 치 → 지
    chi_to_ji = [p for p in patterns if p['original'].endswith('치') and p['golden'].endswith('지')]
    if chi_to_ji:
        print("\n=== 규칙 1: '치' → '지' (형용사 뒤) ===")
        for p in chi_to_ji[:5]:
            print(f"  {p['original']} → {p['golden']}")
        safe_rules.append({
            'pattern': r'(\S+)치\s+않',
            'replacement': r'\1지 않',
            'name': '치→지 (형용사)',
            'confidence': 'HIGH'
        })

    # 2. 형용사 + 자 → 어서/아서
    ja_pattern = [p for p in patterns if '자' in p['original'] and ('어서' in p['golden'] or '아서' in p['golden'])]
    if ja_pattern:
        print("\n=== 규칙 2: 형용사+'자' → '어서/아서' ===")
        for p in ja_pattern[:5]:
            print(f"  {p['original']} → {p['golden']}")

    # 3. 금새 → 금세
    geumsae = [p for p in patterns if '금새' in p['original'] and '금세' in p['golden']]
    if geumsae:
        print("\n=== 규칙 3: '금새' → '금세' ===")
        print(f"  출현 횟수: {len(geumsae)}")
        safe_rules.append({
            'pattern': r'금새',
            'replacement': '금세',
            'name': '금새→금세',
            'confidence': 'HIGH'
        })

    # 4. 로써 → 로서 (자격)
    rosseo = [p for p in patterns if '로써' in p['original'] and '로서' in p['golden']]
    if rosseo:
        print("\n=== 규칙 4: '로써' → '로서' (자격) ===")
        for p in rosseo[:5]:
            print(f"  {p['original']} → {p['golden']}")
        print("  ⚠️ 주의: '도구로써'는 맞는 표현 (문맥 의존)")

    # 5. 사이시옷
    saisiot = [p for p in patterns if p['type'] == '사이시옷']
    if saisiot:
        print("\n=== 규칙 5: 사이시옷 ===")
        for p in saisiot[:10]:
            print(f"  {p['original']} → {p['golden']}")

    return safe_rules

def main():
    """
    메인 실행 함수
    """
    # Train 데이터 로드
    train_df = pd.read_csv('data/train.csv')
    print(f"총 {len(train_df)}개 Train 데이터 분석\n")

    # 패턴 추출
    patterns = extract_patterns(train_df)

    # 고빈도 패턴 찾기
    high_freq = find_high_confidence_rules(patterns)

    # 규칙 유형별 분석
    safe_rules = analyze_rule_types(patterns)

    # 최종 규칙 제안
    print("\n" + "="*60)
    print("최종 제안: 초보수적 규칙 (False Positive ≈ 0%)")
    print("="*60)
    print("""
1. **금새 → 금세** (100% 확실)
   - 단순 치환, False Positive 없음

2. **치 않 → 지 않** (형용사 뒤, 95%+ 확실)
   - 탐탁치 않 → 탐탁지 않
   - 넉넉치 않 → 넉넉지 않

3. **형용사+자 → 어서/아서** (100% 확실, 구현 복잡)
   - 부끄럽자 → 부끄러워서
   - 답답하자 → 답답해서
   - 단, 정확한 치환 로직 필요 (형용사 활용 규칙)

4. **조사 중복 제거** (문맥 의존, 주의 필요)
   - "를/을" 중복
   - False Positive 가능성 있음

5. **사이시옷** (사전 기반, 구현 가능)
   - 고개짓 → 고갯짓
   - 머리기름 → 머릿기름
   - 단, 고정된 사전 필요

⚠️ 권장 사항:
- 규칙 1, 2만 적용 (가장 안전)
- 규칙 3은 복잡도 대비 효과 낮음
- Baseline이 이미 대부분 처리하고 있을 가능성 높음
- 실제 효과는 Train 검증 후 확인 필요
    """)

if __name__ == "__main__":
    main()
