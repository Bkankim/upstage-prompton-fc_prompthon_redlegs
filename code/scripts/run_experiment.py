#!/usr/bin/env python3
"""
통합 실험 실행 스크립트
Train 데이터로 평가 + Test 데이터로 LB 제출 파일 자동 생성

사용 예시:
    uv run python scripts/run_experiment.py --prompt baseline
    uv run python scripts/run_experiment.py --prompt fewshot_v2
    uv run python scripts/run_experiment.py --prompt errortypes_v3
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

# src 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.prompts.registry import get_registry, register_default_prompts, list_prompts


def run_command(cmd, description):
    """
    명령어 실행 및 결과 출력

    Args:
        cmd: 실행할 명령어
        description: 명령어 설명

    Raises:
        SystemExit: 명령어 실행 실패 시
    """
    print(f"\n{'='*60}")
    print(f"[{description}]")
    print(f"Command: {cmd}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"Error in {description}")
        sys.exit(1)

    print(f"{description} completed")
    return result


def main():
    """
    실험 실행 메인 함수

    워크플로우:
    1. Train 데이터로 교정 실행
    2. Train 데이터 평가
    3. Test 데이터로 LB 제출 파일 생성
    4. ID 컬럼 추가
    """
    parser = argparse.ArgumentParser(
        description="Run complete experiment workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_experiment.py --prompt baseline
  python scripts/run_experiment.py --prompt fewshot_v2
  python scripts/run_experiment.py --prompt errortypes_v3 --model solar-pro2
        """
    )

    # 사용 가능한 프롬프트 목록 가져오기
    register_default_prompts()
    available_prompts = list_prompts()

    parser.add_argument(
        "--prompt",
        required=True,
        choices=available_prompts,
        help="Prompt version to use"
    )
    parser.add_argument(
        "--model",
        default="solar-pro2",
        help="Model name (default: solar-pro2)"
    )

    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 출력 경로 설정 (outputs/ 디렉토리 기준)
    train_output = f"outputs/{args.prompt}_train.csv"
    test_output = f"outputs/{args.prompt}_test.csv"
    analysis_output = f"outputs/{args.prompt}_analysis.csv"

    print(f"\nStarting Experiment: {args.prompt}")
    print(f"Timestamp: {timestamp}")

    # outputs 디렉토리 생성
    os.makedirs("outputs", exist_ok=True)

    # 프로젝트 루트 경로
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Step 1: Train 데이터로 교정 실행
    cmd_train = (
        f"cd {project_root} && "
        f"uv run python scripts/generate.py "
        f"--prompt {args.prompt} "
        f"--input data/train_dataset.csv "
        f"--output {train_output} "
        f"--model {args.model}"
    )
    run_command(cmd_train, "Step 1: Generate corrections on TRAIN data")

    # Step 2: Train 데이터 평가
    cmd_eval = (
        f"cd {project_root} && "
        f"uv run python scripts/evaluate.py "
        f"--true_df data/train_dataset.csv "
        f"--pred_df {train_output} "
        f"--output {analysis_output}"
    )
    run_command(cmd_eval, "Step 2: Evaluate on TRAIN data")

    # Step 3: Test 데이터로 LB 제출 파일 생성
    cmd_test = (
        f"cd {project_root} && "
        f"uv run python scripts/generate.py "
        f"--prompt {args.prompt} "
        f"--input data/test.csv "
        f"--output {test_output} "
        f"--model {args.model}"
    )
    run_command(cmd_test, "Step 3: Generate LB submission on TEST data")

    # Step 4: id 컬럼 추가 (test.csv와 병합)
    print(f"\n{'='*60}")
    print("[Step 4: Add ID column to submission]")
    print(f"{'='*60}")

    import pandas as pd

    # 절대 경로로 파일 읽기
    test_csv_path = os.path.join(project_root, 'data', 'test.csv')
    test_output_path = os.path.join(project_root, test_output)

    test_df = pd.read_csv(test_csv_path)
    sub_df = pd.read_csv(test_output_path)

    # id 컬럼이 없으면 추가
    if 'id' not in sub_df.columns:
        final_df = pd.DataFrame({
            'id': test_df['id'],
            'err_sentence': sub_df['err_sentence'],
            'cor_sentence': sub_df['cor_sentence']
        })
        final_df.to_csv(test_output_path, index=False)
        print(f"Added id column to {test_output}")
    else:
        print(f"ID column already exists in {test_output}")

    # 완료 요약
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETED")
    print(f"{'='*60}")
    print(f"Prompt: {args.prompt}")
    print(f"Train evaluation: {analysis_output}")
    print(f"LB submission: {test_output}")
    print(f"\nCheck results:")
    print(f"  - Train performance: cat {analysis_output} | head -5")
    print(f"  - LB file ready: {test_output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
