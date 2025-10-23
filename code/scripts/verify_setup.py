#!/usr/bin/env python3
"""
프로젝트 설정 검증 스크립트

프로젝트 구조, 필수 파일, import 가능 여부 등을 검증합니다.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple


# 색상 코드 (터미널 출력용)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_success(msg: str):
    """성공 메시지 출력"""
    print(f"{GREEN}✓{RESET} {msg}")


def print_error(msg: str):
    """에러 메시지 출력"""
    print(f"{RED}✗{RESET} {msg}")


def print_warning(msg: str):
    """경고 메시지 출력"""
    print(f"{YELLOW}!{RESET} {msg}")


def print_section(title: str):
    """섹션 제목 출력"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def check_directory_structure() -> Tuple[bool, List[str]]:
    """
    디렉토리 구조 검증

    Returns:
        (성공 여부, 에러 메시지 리스트)
    """
    print_section("디렉토리 구조 확인")

    errors = []
    required_dirs = [
        "src",
        "src/prompts",
        "src/metrics",
        "scripts",
        "tests",
        "data",
    ]

    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"{dir_path}/ 존재")
        else:
            print_error(f"{dir_path}/ 누락")
            errors.append(f"Required directory missing: {dir_path}/")

    return len(errors) == 0, errors


def check_required_files() -> Tuple[bool, List[str]]:
    """
    필수 파일 존재 여부 확인

    Returns:
        (성공 여부, 에러 메시지 리스트)
    """
    print_section("필수 파일 확인")

    errors = []
    required_files = [
        # 프롬프트 모듈
        "src/prompts/__init__.py",
        "src/prompts/base.py",
        "src/prompts/baseline.py",
        "src/prompts/fewshot_v2.py",
        "src/prompts/errortypes_v3.py",
        "src/prompts/registry.py",

        # 메트릭 모듈
        "src/metrics/__init__.py",
        "src/metrics/lcs.py",
        "src/metrics/evaluator.py",

        # 핵심 모듈
        "src/__init__.py",
        "src/generator.py",
        "src/evaluator.py",

        # 스크립트
        "scripts/generate.py",
        "scripts/evaluate.py",
        "scripts/run_experiment.py",

        # 테스트
        "tests/__init__.py",
        "tests/test_prompts.py",
        "tests/test_metrics.py",
        "tests/test_generator.py",
        "tests/test_evaluator.py",

        # 설정 파일
        "pyproject.toml",
        ".python-version",
        ".gitignore",

        # 문서
        "README.md",
    ]

    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} 누락")
            errors.append(f"Required file missing: {file_path}")

    return len(errors) == 0, errors


def check_data_files() -> Tuple[bool, List[str]]:
    """
    데이터 파일 확인 (경고만 출력)

    Returns:
        (성공 여부, 경고 메시지 리스트)
    """
    print_section("데이터 파일 확인")

    warnings = []
    data_files = [
        "data/train.csv",
        "data/test.csv",
        "data/sample_submissioncsv.csv",
    ]

    for file_path in data_files:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_warning(f"{file_path} 누락 (선택사항)")
            warnings.append(f"Data file missing: {file_path}")

    return True, warnings


def check_imports() -> Tuple[bool, List[str]]:
    """
    주요 모듈 import 가능 여부 확인

    Returns:
        (성공 여부, 에러 메시지 리스트)
    """
    print_section("모듈 Import 테스트")

    errors = []

    # src 디렉토리를 sys.path에 추가
    sys.path.insert(0, str(Path.cwd()))

    modules_to_test = [
        ("src.prompts.base", "BasePrompt"),
        ("src.prompts.baseline", "BaselinePrompt"),
        ("src.prompts.fewshot_v2", "FewshotV2Prompt"),
        ("src.prompts.errortypes_v3", "ErrorTypesV3Prompt"),
        ("src.prompts.registry", "PromptRegistry"),
        ("src.metrics.lcs", "tokenize"),
        ("src.metrics.evaluator", "evaluate_correction"),
        ("src.generator", "SentenceGenerator"),
        ("src.evaluator", "Evaluator"),
    ]

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_success(f"{module_name}.{class_name} import 성공")
        except ImportError as e:
            print_error(f"{module_name}.{class_name} import 실패: {e}")
            errors.append(f"Import error: {module_name}.{class_name}")
        except AttributeError as e:
            print_error(f"{module_name}.{class_name} 속성 없음: {e}")
            errors.append(f"Attribute error: {module_name}.{class_name}")

    return len(errors) == 0, errors


def check_prompt_registry() -> Tuple[bool, List[str]]:
    """
    프롬프트 레지스트리 확인

    Returns:
        (성공 여부, 에러 메시지 리스트)
    """
    print_section("프롬프트 레지스트리 확인")

    errors = []

    try:
        from src.prompts.registry import get_registry, register_default_prompts

        # 기본 프롬프트 등록
        register_default_prompts()
        registry = get_registry()

        # 등록된 프롬프트 확인
        expected_prompts = ["baseline", "fewshot_v2", "errortypes_v3"]
        registered_prompts = registry.list_prompts()

        print(f"등록된 프롬프트: {registered_prompts}")

        for prompt_name in expected_prompts:
            if prompt_name in registered_prompts:
                print_success(f"'{prompt_name}' 프롬프트 등록됨")
            else:
                print_error(f"'{prompt_name}' 프롬프트 누락")
                errors.append(f"Prompt not registered: {prompt_name}")

        # 각 프롬프트의 to_messages 메서드 테스트
        for prompt_name in expected_prompts:
            if prompt_name in registered_prompts:
                prompt = registry.get(prompt_name)
                try:
                    messages = prompt.to_messages("테스트 문장")
                    if isinstance(messages, list) and len(messages) > 0:
                        print_success(f"'{prompt_name}' to_messages() 동작 확인")
                    else:
                        print_error(f"'{prompt_name}' to_messages() 결과 비정상")
                        errors.append(f"Prompt to_messages error: {prompt_name}")
                except Exception as e:
                    print_error(f"'{prompt_name}' to_messages() 실패: {e}")
                    errors.append(f"Prompt to_messages exception: {prompt_name}")

    except Exception as e:
        print_error(f"레지스트리 확인 실패: {e}")
        errors.append(f"Registry check failed: {e}")

    return len(errors) == 0, errors


def check_env_file() -> Tuple[bool, List[str]]:
    """
    .env 파일 확인 (경고만 출력)

    Returns:
        (성공 여부, 경고 메시지 리스트)
    """
    print_section(".env 파일 확인")

    warnings = []

    if Path(".env").exists():
        print_success(".env 파일 존재")

        # API 키 설정 여부 확인
        with open(".env", "r") as f:
            content = f.read()
            if "UPSTAGE_API_KEY" in content:
                print_success("UPSTAGE_API_KEY 설정됨")
            else:
                print_warning("UPSTAGE_API_KEY 미설정")
                warnings.append(".env file exists but UPSTAGE_API_KEY not set")
    else:
        print_warning(".env 파일 누락 (API 사용 시 필요)")
        warnings.append(".env file not found")

    return True, warnings


def run_simple_integration_test() -> Tuple[bool, List[str]]:
    """
    간단한 통합 테스트 실행

    Returns:
        (성공 여부, 에러 메시지 리스트)
    """
    print_section("간단한 통합 테스트")

    errors = []

    try:
        from src.prompts.registry import get_registry, register_default_prompts
        from src.metrics.lcs import tokenize, find_lcs
        import pandas as pd

        # 1. 프롬프트 레지스트리 테스트
        register_default_prompts()
        registry = get_registry()
        prompt = registry.get("baseline")
        messages = prompt.to_messages("테스트")
        print_success("프롬프트 레지스트리 통합 테스트 통과")

        # 2. LCS 함수 테스트
        tokens1 = tokenize("오늘 날씨가 좋다")
        tokens2 = tokenize("오늘 날씨가 나쁘다")
        lcs = find_lcs(tokens1, tokens2)
        if len(lcs) == 2:  # "오늘", "날씨가" 두 개만 일치
            print_success("LCS 함수 통합 테스트 통과")
        else:
            print_error(f"LCS 함수 결과 비정상 (예상: 2개, 실제: {len(lcs)}개): {lcs}")
            errors.append("LCS function test failed")

        # 3. DataFrame 처리 테스트
        test_df = pd.DataFrame({
            'err_sentence': ['테스트1', '테스트2'],
            'cor_sentence': ['교정1', '교정2']
        })
        print_success("pandas DataFrame 처리 테스트 통과")

    except Exception as e:
        print_error(f"통합 테스트 실패: {e}")
        errors.append(f"Integration test failed: {e}")

    return len(errors) == 0, errors


def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("  프로젝트 설정 검증 시작")
    print("=" * 60)

    all_success = True
    all_errors = []
    all_warnings = []

    # 각 검증 단계 실행
    checks = [
        ("디렉토리 구조", check_directory_structure),
        ("필수 파일", check_required_files),
        ("데이터 파일", check_data_files),
        ("모듈 Import", check_imports),
        ("프롬프트 레지스트리", check_prompt_registry),
        (".env 파일", check_env_file),
        ("통합 테스트", run_simple_integration_test),
    ]

    for check_name, check_func in checks:
        success, messages = check_func()
        if not success:
            all_success = False
            all_errors.extend(messages)
        else:
            # 경고 메시지 수집
            if check_name in ["데이터 파일", ".env 파일"]:
                all_warnings.extend(messages)

    # 최종 결과 출력
    print_section("검증 결과 요약")

    if all_success:
        print_success("모든 필수 검증 항목 통과!")
    else:
        print_error(f"검증 실패: {len(all_errors)}개 오류 발견")
        for error in all_errors:
            print(f"  - {error}")

    if all_warnings:
        print(f"\n경고: {len(all_warnings)}개")
        for warning in all_warnings:
            print_warning(warning)

    print("\n" + "=" * 60)

    # 종료 코드 반환
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
