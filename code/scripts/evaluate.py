"""
평가 실행 스크립트
정답 CSV와 예측 CSV를 비교하여 Recall, Precision 계산

사용 예시:
    uv run python scripts/evaluate.py --true_df data/train_dataset.csv --pred_df submission.csv
    uv run python scripts/evaluate.py --true_df data/train_dataset.csv --pred_df submission.csv --output analysis.csv
"""

import sys
import os
import argparse

# src 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from src.evaluator import Evaluator


def main():
    """
    평가 스크립트 메인 함수
    """
    parser = argparse.ArgumentParser(
        description="Evaluate submission against truth using metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/evaluate.py --true_df data/train_dataset.csv --pred_df submission.csv
  python scripts/evaluate.py --true_df data/train_dataset.csv --pred_df submission.csv --output analysis.csv
        """
    )

    parser.add_argument(
        "--true_df",
        default="data/train_dataset.csv",
        help="Path to ground truth CSV containing err_sentence, cor_sentence"
    )
    parser.add_argument(
        "--pred_df",
        default="submission.csv",
        help="Path to submission CSV containing cor_sentence"
    )
    parser.add_argument(
        "--output",
        default="analysis.csv",
        help="Path to save analysis DataFrame as CSV (optional)"
    )

    args = parser.parse_args()

    # CSV 파일 로드
    try:
        true_df = pd.read_csv(args.true_df)
        print(f"Loaded truth data: {args.true_df} ({len(true_df)} rows)")
    except FileNotFoundError:
        print(f"Error: Truth file not found: {args.true_df}")
        sys.exit(1)

    try:
        pred_df = pd.read_csv(args.pred_df)
        print(f"Loaded prediction data: {args.pred_df} ({len(pred_df)} rows)")
    except FileNotFoundError:
        print(f"Error: Prediction file not found: {args.pred_df}")
        sys.exit(1)

    # 평가 수행
    try:
        evaluator = Evaluator()
        results = evaluator.evaluate(true_df, pred_df)

        # 분석 결과 저장
        if args.output:
            results['analysis_df'].to_csv(args.output, index=False)
            print(f"\nAnalysis results saved to {args.output}")

    except Exception as e:
        print(f"Error during evaluation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
