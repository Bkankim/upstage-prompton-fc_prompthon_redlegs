"""
Phase 6: Test 데이터 교정 및 LB 제출 파일 생성

목표:
- Test 109개 전체 교정 (fewshot_v3 + EnhancedPostprocessor)
- LB 제출 파일 생성 및 검증
- 메타데이터/길이 폭발/숫자 분리 체크
"""

import pandas as pd
import json
import re
from pathlib import Path
from src.generator import SentenceGenerator


def detect_metadata(text):
    """
    메타데이터 패턴 탐지
    """
    if pd.isna(text):
        return False
    metadata_patterns = [
        r'※', r'지시사항', r'설명', r'참고',
        r'원문:', r'교정:', r'수정:', r'결과:',
        r'<원문>', r'<교정>',
        r'\[최종', r'\[재최종', r'\[시스템',
        r'규칙.*따라', r'추가.*지시'
    ]
    for pattern in metadata_patterns:
        if re.search(pattern, text):
            return True
    return False


def check_number_separation(original, corrected):
    """
    숫자 분리 체크 (예: "1.4%" → "1. 4%")
    """
    # 소수점 숫자 패턴
    original_decimals = re.findall(r'\d+\.\d+', original)
    corrected_decimals = re.findall(r'\d+\.\d+', corrected)

    # 원문에 있던 소수점이 사라졌는지 확인
    if len(original_decimals) > len(corrected_decimals):
        # 분리된 패턴이 있는지 확인 ("1. 4")
        separated = re.findall(r'\d+\.\s+\d+', corrected)
        if separated:
            return True, separated

    return False, []


def generate_test_submission():
    """
    Test 데이터 교정 및 제출 파일 생성
    """
    print("="*70)
    print("Phase 6: Test LB 제출 파일 생성")
    print("="*70)
    print()

    # Test 데이터 로드
    test_df = pd.read_csv(Path(__file__).parent / "data" / "test.csv")

    print(f"Test 샘플: {len(test_df)}개")
    print()

    # Generator 초기화
    print("프롬프트: fewshot_v3 (검증된 원본)")
    print("후처리: EnhancedPostprocessor (개선판)")
    print()

    generator = SentenceGenerator(
        prompt_name='fewshot_v3',
        enable_postprocessing=True,
        use_enhanced_postprocessor=True
    )

    # 교정 실행
    print(f"교정 진행 중... (API 호출 {len(test_df)}회, 예상 시간: 5-8분)")
    print()

    corrections = []
    for idx, row in test_df.iterrows():
        err_text = row['err_sentence']

        # API 호출
        corrected = generator.generate_single(err_text)

        corrections.append({
            'id': row['id'],
            'err_sentence': err_text,
            'cor_sentence': corrected
        })

        # 진행 상황 출력 (매 25개마다)
        if len(corrections) % 25 == 0:
            print(f"  [{len(corrections)}/{len(test_df)}] 완료... ({len(corrections)/len(test_df)*100:.1f}%)")

    print(f"  [{len(corrections)}/{len(test_df)}] 완료! (100.0%)")
    print()

    # DataFrame 변환
    submission_df = pd.DataFrame(corrections)

    # 검증 로직
    print("="*70)
    print("제출 파일 검증")
    print("="*70)
    print()

    # 1. 메타데이터 체크
    metadata_mask = submission_df['cor_sentence'].apply(detect_metadata)
    metadata_count = metadata_mask.sum()

    print(f"1. 메타데이터 탐지: {metadata_count}개")
    if metadata_count > 0:
        print(f"   ⚠️ 메타데이터 의심 케이스:")
        for idx in submission_df[metadata_mask].index[:5]:  # 최대 5개만 출력
            row = submission_df.loc[idx]
            print(f"   - ID {row['id']}: {row['cor_sentence'][:50]}...")
    else:
        print(f"   ✅ 메타데이터 없음")
    print()

    # 2. 길이 폭발 체크
    submission_df['length_ratio'] = submission_df.apply(
        lambda row: len(row['cor_sentence']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )
    length_explosion_mask = submission_df['length_ratio'] > 1.5
    length_explosion_count = length_explosion_mask.sum()

    print(f"2. 길이 폭발 (>150%): {length_explosion_count}개")
    if length_explosion_count > 0:
        print(f"   ⚠️ 길이 폭발 케이스:")
        for idx in submission_df[length_explosion_mask].index[:5]:
            row = submission_df.loc[idx]
            print(f"   - ID {row['id']}: {row['length_ratio']:.1%} ({len(row['err_sentence'])}자 → {len(row['cor_sentence'])}자)")
    else:
        print(f"   ✅ 길이 폭발 없음")
    print()

    # 3. 숫자 분리 체크
    number_separation_issues = []
    for idx, row in submission_df.iterrows():
        is_separated, separated_patterns = check_number_separation(
            row['err_sentence'],
            row['cor_sentence']
        )
        if is_separated:
            number_separation_issues.append({
                'id': row['id'],
                'patterns': separated_patterns
            })

    print(f"3. 숫자 분리 체크: {len(number_separation_issues)}개")
    if number_separation_issues:
        print(f"   ⚠️ 숫자 분리 의심 케이스:")
        for issue in number_separation_issues[:5]:
            print(f"   - ID {issue['id']}: {issue['patterns']}")
    else:
        print(f"   ✅ 숫자 분리 없음")
    print()

    # 4. 형식 체크
    print(f"4. 형식 체크:")
    print(f"   - 컬럼: {list(submission_df.columns)}")
    print(f"   - ID 범위: {submission_df['id'].min()} ~ {submission_df['id'].max()}")
    print(f"   - 결측치: {submission_df.isnull().sum().sum()}개")

    if list(submission_df.columns) == ['id', 'err_sentence', 'cor_sentence']:
        print(f"   ✅ 형식 정상")
    else:
        print(f"   ❌ 형식 오류! 컬럼 순서 확인 필요")
    print()

    # 통계 요약
    print("="*70)
    print("통계 요약")
    print("="*70)
    print()
    print(f"평균 길이 비율: {submission_df['length_ratio'].mean():.1%}")
    print(f"최대 길이 비율: {submission_df['length_ratio'].max():.1%}")
    print(f"최소 길이 비율: {submission_df['length_ratio'].min():.1%}")
    print()

    # 최종 판정
    print("="*70)
    print("최종 판정")
    print("="*70)
    print()

    issues = []
    if metadata_count > 5:
        issues.append(f"메타데이터 과다 ({metadata_count}개)")
    if length_explosion_count > 10:
        issues.append(f"길이 폭발 과다 ({length_explosion_count}개)")
    if len(number_separation_issues) > 5:
        issues.append(f"숫자 분리 과다 ({len(number_separation_issues)}개)")

    if not issues:
        print("✅ 제출 파일 검증 통과!")
        print("   → LB 제출 준비 완료")
    else:
        print("⚠️ 검토 필요 항목:")
        for issue in issues:
            print(f"   - {issue}")
        print("   → 수동 검토 권장")
    print()

    # 파일 저장
    output_dir = Path(__file__).parent / "outputs" / "submissions" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "submission_fewshot_v3_enhanced_test.csv"

    # 제출용 파일 (length_ratio 컬럼 제거)
    submission_df[['id', 'err_sentence', 'cor_sentence']].to_csv(
        output_path,
        index=False,
        encoding='utf-8'
    )

    print(f"제출 파일 저장: {output_path}")
    print()

    # 검증용 상세 파일 (length_ratio 포함)
    detail_path = output_dir / "submission_fewshot_v3_enhanced_test_detail.csv"
    submission_df.to_csv(detail_path, index=False, encoding='utf-8')
    print(f"검증용 상세 파일: {detail_path}")
    print()

    # 후처리 로그 저장
    if hasattr(generator.postprocessor, 'save_processing_log'):
        log_path = Path(__file__).parent / "outputs" / "analysis" / "test_submission_postprocess_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        generator.postprocessor.save_processing_log(str(log_path))
        print(f"후처리 로그: {log_path}")

    print()
    print("="*70)
    print("Phase 6 완료!")
    print("="*70)

    return submission_df, output_path


if __name__ == "__main__":
    submission_df, output_path = generate_test_submission()

    print()
    print(f"다음 단계: {output_path} 파일을 LB에 제출하세요.")
