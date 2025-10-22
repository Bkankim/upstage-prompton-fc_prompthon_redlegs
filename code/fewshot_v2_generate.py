"""
Few-shot v2 프롬프트 생성 스크립트 (레거시 래퍼)
scripts/generate.py를 fewshot_v2 프롬프트로 호출

하위 호환성을 위한 래퍼 스크립트
"""

import sys
import os
import subprocess
import argparse


def main():
    """
    Few-shot v2 프롬프트로 통합 생성기 호출
    조사, 표준어, 사이시옷, 능동피동, 문법 예시 포함
    """
    parser = argparse.ArgumentParser(description="Generate corrected sentences using Few-shot v2 prompt")
    parser.add_argument("--input", default="data/train_dataset.csv", help="Input CSV path containing err_sentence column")
    parser.add_argument("--output", default="submission_fewshot_v2.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name (default: solar-pro2)")
    args = parser.parse_args()

    # scripts/generate.py 경로
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "generate.py")

    # 통합 생성기 호출 (fewshot_v2 프롬프트 사용)
    cmd = [
        sys.executable,
        script_path,
        "--prompt", "fewshot_v2",
        "--input", args.input,
        "--output", args.output,
        "--model", args.model
    ]

    # 서브프로세스 실행
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
