"""
문장 생성기 통합 모듈
프롬프트 레지스트리를 사용하여 다양한 프롬프트로 문장 교정 수행
"""

import os
from typing import Optional, List

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

from src.prompts.registry import get_registry, register_default_prompts
from src.postprocessors.rule_checklist import RuleChecklistPostprocessor
from src.postprocessors.enhanced_postprocessor import EnhancedPostprocessor


class SentenceGenerator:
    """
    문장 교정 생성기 클래스
    프롬프트 레지스트리를 통해 다양한 프롬프트 전략 지원
    """

    def __init__(
        self,
        prompt_name: str,
        model: str = "solar-pro2",
        api_key: Optional[str] = None,
        enable_postprocessing: bool = True,
        use_enhanced_postprocessor: bool = False
    ):
        """
        생성기 초기화

        Args:
            prompt_name: 사용할 프롬프트 이름 (registry에서 조회)
            model: 사용할 모델 이름 (기본값: solar-pro2)
            api_key: Upstage API 키 (None인 경우 환경변수에서 로드)
            enable_postprocessing: 후처리 활성화 여부 (기본값: True)
            use_enhanced_postprocessor: Enhanced 후처리 사용 여부 (기본값: False)

        Raises:
            ValueError: API 키가 없거나 프롬프트를 찾을 수 없는 경우
        """
        # 환경변수 로드
        load_dotenv()

        # API 키 설정
        if api_key is None:
            api_key = os.getenv("UPSTAGE_API_KEY")

        if not api_key:
            raise ValueError(
                "UPSTAGE_API_KEY not found. "
                "Set it in .env file or pass as argument."
            )

        # 프롬프트 레지스트리에서 프롬프트 조회
        register_default_prompts()
        registry = get_registry()

        self.prompt = registry.get(prompt_name)
        if self.prompt is None:
            available = registry.list_prompts()
            raise ValueError(
                f"Prompt '{prompt_name}' not found in registry. "
                f"Available prompts: {available}"
            )

        # OpenAI 클라이언트 초기화 (Upstage API 사용)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        )

        self.model = model
        self.prompt_name = prompt_name
        self.enable_postprocessing = enable_postprocessing
        self.use_enhanced_postprocessor = use_enhanced_postprocessor

        # 후처리 모듈 초기화
        if enable_postprocessing:
            if use_enhanced_postprocessor:
                self.postprocessor = EnhancedPostprocessor(enable_logging=True)
            else:
                self.postprocessor = RuleChecklistPostprocessor()
        else:
            self.postprocessor = None

    def _apply_postprocessing(self, original: str, corrected: str) -> str:
        """
        후처리 적용

        Args:
            original: 원문 텍스트
            corrected: 교정된 텍스트

        Returns:
            str: 후처리된 텍스트
        """
        if self.postprocessor is None:
            return corrected

        try:
            return self.postprocessor.process(original, corrected)
        except Exception as e:
            print(f"Warning: Postprocessing failed - {e}")
            return corrected

    def generate_single(self, text: str) -> str:
        """
        단일 문장 교정 생성

        Args:
            text: 교정할 원문 텍스트

        Returns:
            str: 교정된 문장 (실패 시 원문 반환)
        """
        try:
            # 프롬프트를 OpenAI 메시지 포맷으로 변환
            messages = self.prompt.to_messages(text)

            # API 호출
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
            )

            corrected = resp.choices[0].message.content.strip()

            # 후처리 적용
            final = self._apply_postprocessing(text, corrected)

            return final

        except Exception as e:
            print(f"Error processing: {text[:50]}... - {e}")
            return text  # fallback to original

    def generate_batch(self, err_sentences: List[str]) -> pd.DataFrame:
        """
        여러 문장을 배치로 교정

        Args:
            err_sentences: 교정할 문장 리스트

        Returns:
            pd.DataFrame: err_sentence, cor_sentence 컬럼을 가진 데이터프레임
        """
        err_results = []
        cor_results = []

        for text in tqdm(err_sentences, desc=f"Generating ({self.prompt_name})"):
            err_results.append(text)
            corrected = self.generate_single(text)
            cor_results.append(corrected)

        return pd.DataFrame({
            "err_sentence": err_results,
            "cor_sentence": cor_results
        })

    def generate_from_csv(
        self,
        input_path: str,
        output_path: str
    ) -> None:
        """
        CSV 파일에서 문장을 읽어 교정하고 결과를 저장

        Args:
            input_path: 입력 CSV 파일 경로 (err_sentence 컬럼 필수)
            output_path: 출력 CSV 파일 경로

        Raises:
            ValueError: err_sentence 컬럼이 없는 경우
        """
        # 입력 파일 읽기
        df = pd.read_csv(input_path)

        if "err_sentence" not in df.columns:
            raise ValueError("Input CSV must contain 'err_sentence' column")

        print(f"Prompt: {self.prompt_name}")
        print(f"Model: {self.model}")
        print(f"Input: {input_path}")
        print(f"Output: {output_path}")

        # 문장 교정 실행
        err_sentences = df["err_sentence"].astype(str).tolist()
        result_df = self.generate_batch(err_sentences)

        # 결과 저장
        result_df.to_csv(output_path, index=False)
        print(f"Wrote {len(result_df)} rows to {output_path}")
