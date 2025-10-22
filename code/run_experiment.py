#!/usr/bin/env python3
"""
통합 실험 실행 스크립트 (레거시 래퍼)

하위 호환성을 위한 래퍼 스크립트입니다.
실제 구현은 scripts/run_experiment.py에 있습니다.

사용 예시:
    uv run python run_experiment.py --prompt baseline
    uv run python run_experiment.py --prompt fewshot_v2
"""

import os
import sys
import subprocess


def main():
    """
    scripts/run_experiment.py를 호출하는 래퍼
    """
    # 현재 스크립트의 디렉토리 경로
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # scripts/run_experiment.py 경로
    target_script = os.path.join(script_dir, "scripts", "run_experiment.py")

    # 인자를 그대로 전달하여 실행
    cmd = [sys.executable, target_script] + sys.argv[1:]

    # 실행 및 결과 반환
    result = subprocess.run(cmd, cwd=script_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
