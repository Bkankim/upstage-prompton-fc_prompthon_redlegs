"""
통합 문장 생성 스크립트
프롬프트 레지스트리를 활용한 범용 생성기

사용 예시:
    uv run python scripts/generate.py --prompt baseline --input data/train.csv --output outputs/baseline.csv
    uv run python scripts/generate.py --prompt fewshot_v2 --input data/test.csv --output outputs/fewshot.csv
"""

import sys
import os
import argparse

# src 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.generator import SentenceGenerator
from src.prompts.registry import get_registry, register_default_prompts


def main():
    """
    통합 생성 스크립트 실행
    """
    parser = argparse.ArgumentParser(
        description="Generate corrected sentences using various prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate.py --prompt baseline --input data/train.csv --output baseline.csv
  python scripts/generate.py --prompt fewshot_v2 --input data/test.csv --output fewshot.csv
  python scripts/generate.py --prompt errortypes_v3 --input data/train.csv --output errors.csv
        """
    )

    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available prompts and exit"
    )
    parser.add_argument(
        "--prompt",
        help="Prompt name to use (e.g., baseline, fewshot_v2, errortypes_v3)"
    )
    parser.add_argument(
        "--input",
        default="data/train_dataset.csv",
        help="Input CSV path containing err_sentence column"
    )
    parser.add_argument(
        "--output",
        default="submission.csv",
        help="Output CSV path"
    )
    parser.add_argument(
        "--model",
        default="solar-pro2",
        help="Model name (default: solar-pro2)"
    )
    parser.add_argument(
        "--no-postprocess",
        action="store_true",
        help="Disable postprocessing (no rule application, metadata only)"
    )

    args = parser.parse_args()

    # 사용 가능한 프롬프트 목록 출력
    if args.list_prompts:
        register_default_prompts()
        registry = get_registry()
        prompts = registry.list_prompts()
        print("Available prompts:")
        for prompt_name in prompts:
            print(f"  - {prompt_name}")
        return

    # 프롬프트 인자 필수 검증
    if not args.prompt:
        parser.error("--prompt is required when not using --list-prompts")

    # 생성기 초기화 및 실행
    try:
        generator = SentenceGenerator(
            prompt_name=args.prompt,
            model=args.model,
            enable_postprocessing=not args.no_postprocess
        )

        print(f"Postprocessing: {'Disabled' if args.no_postprocess else 'Enabled'}")

        generator.generate_from_csv(
            input_path=args.input,
            output_path=args.output
        )

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
