#!/usr/bin/env python3
"""
통합 실험 실행 스크립트
Train 데이터로 평가 + Test 데이터로 LB 제출 파일 자동 생성
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime

def run_command(cmd, description):
    """
    명령어 실행 및 결과 출력
    """
    print(f"\n{'='*60}")
    print(f"[{description}]")
    print(f"Command: {cmd}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"❌ Error in {description}")
        sys.exit(1)

    print(f"✅ {description} completed")
    return result

def main():
    """
    실험 실행 메인 함수
    1. Train 데이터로 교정 실행
    2. Train 데이터 평가
    3. Test 데이터로 LB 제출 파일 생성
    """
    parser = argparse.ArgumentParser(description="Run complete experiment workflow")
    parser.add_argument("--prompt", required=True,
                       choices=["baseline", "fewshot_v2", "errortypes_v3", "cot_v4", "multiturn_v5"],
                       help="Prompt version to use")
    parser.add_argument("--model", default="solar-pro2", help="Model name")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 파일명 설정
    if args.prompt == "baseline":
        script = "baseline_generate.py"
        train_output = "submission_baseline.csv"
        test_output = f"submissions/submission_baseline_test.csv"
        analysis_output = "analysis_baseline.csv"
    elif args.prompt == "fewshot_v2":
        script = "fewshot_v2_generate.py"
        train_output = "submission_fewshot_v2.csv"
        test_output = f"submissions/submission_fewshot_v2_test.csv"
        analysis_output = "analysis_fewshot_v2.csv"
    elif args.prompt == "errortypes_v3":
        script = "errortypes_v3_generate.py"
        train_output = "submission_errortypes_v3.csv"
        test_output = f"submissions/submission_errortypes_v3_test.csv"
        analysis_output = "analysis_errortypes_v3.csv"
    elif args.prompt == "cot_v4":
        script = "cot_v4_generate.py"
        train_output = "submission_cot_v4.csv"
        test_output = f"submissions/submission_cot_v4_test.csv"
        analysis_output = "analysis_cot_v4.csv"
    elif args.prompt == "multiturn_v5":
        script = "multiturn_v5_generate.py"
        train_output = "submission_multiturn_v5.csv"
        test_output = f"submissions/submission_multiturn_v5_test.csv"
        analysis_output = "analysis_multiturn_v5.csv"

    print(f"\n🚀 Starting Experiment: {args.prompt}")
    print(f"Timestamp: {timestamp}")

    # submissions 디렉토리 생성
    os.makedirs("submissions", exist_ok=True)

    # Step 1: Train 데이터로 교정 실행
    cmd_train = f"uv run python {script} --input data/train_dataset.csv --output {train_output} --model {args.model}"
    run_command(cmd_train, "Step 1: Generate corrections on TRAIN data")

    # Step 2: Train 데이터 평가
    cmd_eval = f"uv run python evaluate.py --true_df data/train_dataset.csv --pred_df {train_output} --output {analysis_output}"
    run_command(cmd_eval, "Step 2: Evaluate on TRAIN data")

    # Step 3: Test 데이터로 LB 제출 파일 생성
    cmd_test = f"uv run python {script} --input data/test.csv --output {test_output} --model {args.model}"
    run_command(cmd_test, "Step 3: Generate LB submission on TEST data")

    # Step 4: id 컬럼 추가 (test.csv와 병합)
    print(f"\n{'='*60}")
    print("[Step 4: Add ID column to submission]")
    print(f"{'='*60}")

    import pandas as pd
    test_df = pd.read_csv('data/test.csv')
    sub_df = pd.read_csv(test_output)

    # id 컬럼이 없으면 추가
    if 'id' not in sub_df.columns:
        final_df = pd.DataFrame({
            'id': test_df['id'],
            'err_sentence': sub_df['err_sentence'],
            'cor_sentence': sub_df['cor_sentence']
        })
        final_df.to_csv(test_output, index=False)
        print(f"✅ Added id column to {test_output}")
    else:
        print(f"✅ ID column already exists in {test_output}")

    # 완료 요약
    print(f"\n{'='*60}")
    print("🎉 EXPERIMENT COMPLETED")
    print(f"{'='*60}")
    print(f"Prompt: {args.prompt}")
    print(f"Train evaluation: {analysis_output}")
    print(f"LB submission: {test_output}")
    print(f"\n📊 Check results:")
    print(f"  - Train performance: cat {analysis_output} | head -5")
    print(f"  - LB file ready: {test_output}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
