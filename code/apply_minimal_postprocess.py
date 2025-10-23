"""
최소 후처리 스크립트 (메타데이터만 제거, 문법 규칙 제외)

원본 API 응답에서 메타데이터만 제거하여
순수 규칙 효과 측정을 위한 베이스라인 생성
"""

import pandas as pd
import re
from pathlib import Path


def clean_metadata_only(text: str) -> str:
    """
    메타데이터만 제거 (문법 규칙은 적용하지 않음)

    Args:
        text: 원본 API 응답

    Returns:
        메타데이터가 제거된 텍스트
    """
    if not text or not isinstance(text, str):
        return text

    # 레이블 제거 (교정:, 수정:, 결과: 등)
    text = re.sub(r'^(교정|수정|결과|답변|정답)\s*[:：]\s*', '', text, flags=re.MULTILINE)

    # 번호 리스트 제거 (1., 2., -, * 등으로 시작하는 줄)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # 번호 리스트나 불릿 포인트로 시작하지 않는 줄만 유지
        if not re.match(r'^\s*[\d\-\*\.]+\s+', line):
            cleaned_lines.append(line)

    # 줄바꿈 유지하며 재결합
    text = '\n'.join(cleaned_lines)

    # 따옴표 제거 (처음과 끝의 따옴표만)
    text = re.sub(r'^["\'「『](.*)["\'」』]$', r'\1', text.strip())

    # XML/HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)

    # "원문 : 교정문" 형식 처리
    # 예: "원문입니다. : 교정된 문장입니다."
    # 콜론 뒤 부분만 추출
    # 주의: 비율(7:3), 시간(3:00) 등 정상 콜론은 제외
    if ':' in text or '：' in text:
        # 비율/시간 패턴이 있으면 스킵
        if not re.search(r'\d+\s*[：:]\s*\d+', text):
            # 메타데이터 콜론 확인: 앞부분(30% 이내)에 키워드 존재
            colon_pos = text.find(':')
            if colon_pos < 0:
                colon_pos = text.find('：')

            if colon_pos > 0 and colon_pos / len(text) < 0.3:
                before_colon = text[:colon_pos].strip()
                keywords = ['원문', '교정', '수정', '결과', '답변', '정답']
                if any(kw in before_colon for kw in keywords):
                    # 메타데이터로 판단 - 콜론 뒤 부분만 추출
                    parts = re.split(r'\s*[：:]\s*', text, maxsplit=1)
                    if len(parts) == 2:
                        text = parts[1]

    # 괄호 안 설명문 제거 (※, 주의, 참고 등)
    # 예: "(※ 원문의 맞춤법과 문법이...)"
    text = re.sub(r'\s*\([※주참].+?\)', '', text)
    text = re.sub(r'\s*\(원문.+?\)', '', text)
    text = re.sub(r'\s*\(수정.+?\)', '', text)
    text = re.sub(r'\s*\(교정.+?\)', '', text)
    text = re.sub(r'\s*\(예:.+?\)', '', text)

    # ** 강조 문구 제거
    # 예: "**수정 사항 없음**"
    text = re.sub(r'\*\*[^*]+\*\*', '', text)

    # 기타 설명 문구 제거
    text = re.sub(r'수정\s*사항\s*없음', '', text, flags=re.IGNORECASE)
    text = re.sub(r'수정\s*불필요', '', text, flags=re.IGNORECASE)
    text = re.sub(r'교정\s*불필요', '', text, flags=re.IGNORECASE)
    text = re.sub(r'이미\s*정확', '', text, flags=re.IGNORECASE)

    # 줄바꿈을 공백으로 변환
    text = text.replace('\n', ' ')

    # 연속된 공백을 하나로
    text = re.sub(r'\s+', ' ', text)

    # 앞뒤 공백 제거
    text = text.strip()

    return text


def process_file(input_path: Path, output_path: Path):
    """
    CSV 파일의 교정 결과에 최소 후처리 적용

    Args:
        input_path: 입력 CSV (원본 API 응답)
        output_path: 출력 CSV (메타데이터만 제거)
    """
    # 데이터 로드
    df = pd.read_csv(input_path)

    print(f"입력: {input_path}")
    print(f"출력: {output_path}")
    print(f"처리할 행: {len(df)}개")

    # 메타데이터만 제거
    cleaned = []
    for idx, text in enumerate(df['cor_sentence']):
        cleaned_text = clean_metadata_only(str(text))
        cleaned.append(cleaned_text)

        if (idx + 1) % 50 == 0:
            print(f"진행: {idx + 1}/{len(df)}")

    # 결과 저장
    result_df = pd.DataFrame({
        'err_sentence': df['err_sentence'],
        'cor_sentence': cleaned
    })

    result_df.to_csv(output_path, index=False)
    print(f"\n✅ 완료: {output_path}")

    # 통계 출력
    changed = sum(1 for i in range(len(df)) if df['cor_sentence'].iloc[i] != cleaned[i])
    print(f"변경된 케이스: {changed}/{len(df)} ({changed/len(df)*100:.1f}%)")


def main():
    """메인 실행"""
    code_dir = Path(__file__).parent

    # 입출력 경로
    input_path = code_dir / "outputs" / "submissions" / "train" / "submission_baseline_no_rules_raw.csv"
    output_path = code_dir / "outputs" / "submissions" / "train" / "submission_baseline_no_rules.csv"

    # 파일 존재 확인
    if not input_path.exists():
        print(f"오류: {input_path} 파일이 없습니다.")
        print("먼저 --no-postprocess로 생성해주세요.")
        return

    # 처리 실행
    process_file(input_path, output_path)


if __name__ == "__main__":
    main()
