"""
SentenceGenerator 클래스 테스트
Mock을 사용하여 API 호출 없이 테스트
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.generator import SentenceGenerator


class TestSentenceGeneratorInit:
    """SentenceGenerator 초기화 테스트"""

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_init_with_valid_prompt(self, mock_openai):
        """유효한 프롬프트로 초기화 테스트"""
        generator = SentenceGenerator(prompt_name="baseline")

        assert generator is not None
        assert generator.prompt_name == "baseline"
        assert generator.model == "solar-pro2"

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_init_with_invalid_prompt(self, mock_openai):
        """존재하지 않는 프롬프트로 초기화 시 예외 발생 테스트"""
        with pytest.raises(ValueError) as exc_info:
            SentenceGenerator(prompt_name="nonexistent_prompt")

        assert "not found in registry" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.generator.load_dotenv')  # .env 파일 로드 차단
    def test_init_without_api_key(self, mock_load_dotenv):
        """API 키 없이 초기화 시 예외 발생 테스트"""
        # load_dotenv를 mock하여 .env 파일 로드 차단
        mock_load_dotenv.return_value = None

        with pytest.raises(ValueError) as exc_info:
            SentenceGenerator(prompt_name="baseline")

        assert "UPSTAGE_API_KEY not found" in str(exc_info.value)

    @patch('src.generator.OpenAI')
    def test_init_with_explicit_api_key(self, mock_openai):
        """명시적으로 API 키를 전달하여 초기화 테스트"""
        generator = SentenceGenerator(
            prompt_name="baseline",
            api_key="explicit-test-key"
        )

        assert generator is not None

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_init_with_custom_model(self, mock_openai):
        """커스텀 모델 지정 테스트"""
        generator = SentenceGenerator(
            prompt_name="baseline",
            model="custom-model"
        )

        assert generator.model == "custom-model"


class TestSentenceGeneratorSingle:
    """generate_single 메서드 테스트"""

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_single_success(self, mock_openai):
        """정상적인 단일 문장 생성 테스트"""
        # Mock OpenAI 응답 설정
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "교정된 문장"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        result = generator.generate_single("오늘 날씨가 않좋다")

        assert result == "교정된 문장"
        assert mock_client.chat.completions.create.called

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_single_with_whitespace(self, mock_openai):
        """공백이 포함된 응답 처리 테스트"""
        # Mock OpenAI 응답 (앞뒤 공백 포함)
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "  교정된 문장  "

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        result = generator.generate_single("테스트 문장")

        # strip()이 적용되어야 함
        assert result == "교정된 문장"

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_single_api_error(self, mock_openai):
        """API 에러 발생 시 원문 반환 테스트"""
        # Mock API 에러
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        original_text = "오늘 날씨가 않좋다"
        result = generator.generate_single(original_text)

        # 에러 발생 시 원문 반환
        assert result == original_text

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_single_calls_with_correct_params(self, mock_openai):
        """API 호출 시 올바른 파라미터 전달 테스트"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "교정됨"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        generator.generate_single("테스트")

        # API 호출 확인
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "solar-pro2"
        assert call_args[1]['temperature'] == 0.0
        assert 'messages' in call_args[1]


class TestSentenceGeneratorBatch:
    """generate_batch 메서드 테스트"""

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_batch_success(self, mock_openai):
        """배치 생성 성공 테스트"""
        # Mock OpenAI 응답
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "교정됨"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        sentences = ["문장1", "문장2", "문장3"]

        result_df = generator.generate_batch(sentences)

        # DataFrame 형태 확인
        assert isinstance(result_df, pd.DataFrame)
        assert "err_sentence" in result_df.columns
        assert "cor_sentence" in result_df.columns
        assert len(result_df) == 3

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_batch_empty_list(self, mock_openai):
        """빈 리스트로 배치 생성 테스트"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        result_df = generator.generate_batch([])

        # 빈 DataFrame 반환
        assert len(result_df) == 0
        assert "err_sentence" in result_df.columns
        assert "cor_sentence" in result_df.columns

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_generate_batch_preserves_order(self, mock_openai):
        """배치 생성 시 순서 보존 테스트"""
        # 각 문장마다 다른 응답 반환
        def mock_create(*args, **kwargs):
            response = MagicMock()
            message = kwargs['messages'][-1]['content']
            response.choices[0].message.content = f"교정_{message}"
            return response

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = mock_create
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        sentences = ["문장A", "문장B", "문장C"]

        result_df = generator.generate_batch(sentences)

        # 순서 확인
        assert result_df["err_sentence"].tolist() == sentences


class TestSentenceGeneratorFromCSV:
    """generate_from_csv 메서드 테스트"""

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    @patch('pandas.DataFrame.to_csv')
    @patch('pandas.read_csv')
    def test_generate_from_csv_success(self, mock_read_csv, mock_to_csv, mock_openai):
        """CSV 파일 처리 성공 테스트"""
        # Mock 입력 CSV
        mock_input_df = pd.DataFrame({
            'err_sentence': ['문장1', '문장2']
        })
        mock_read_csv.return_value = mock_input_df

        # Mock OpenAI 응답
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "교정됨"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")
        generator.generate_from_csv("input.csv", "output.csv")

        # to_csv 호출 확인
        assert mock_to_csv.called

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    @patch('pandas.read_csv')
    def test_generate_from_csv_missing_column(self, mock_read_csv, mock_openai):
        """err_sentence 컬럼이 없는 CSV 처리 시 예외 발생 테스트"""
        # Mock 입력 CSV (err_sentence 컬럼 없음)
        mock_input_df = pd.DataFrame({
            'wrong_column': ['문장1', '문장2']
        })
        mock_read_csv.return_value = mock_input_df

        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")

        with pytest.raises(ValueError) as exc_info:
            generator.generate_from_csv("input.csv", "output.csv")

        assert "err_sentence" in str(exc_info.value)


class TestSentenceGeneratorPromptSelection:
    """다양한 프롬프트 선택 테스트"""

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_baseline_prompt_selection(self, mock_openai):
        """baseline 프롬프트 선택 테스트"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="baseline")

        assert generator.prompt.name == "baseline"

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_fewshot_v2_prompt_selection(self, mock_openai):
        """fewshot_v2 프롬프트 선택 테스트"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="fewshot_v2")

        assert generator.prompt.name == "fewshot_v2"

    @patch.dict(os.environ, {'UPSTAGE_API_KEY': 'test-key'})
    @patch('src.generator.OpenAI')
    def test_errortypes_v3_prompt_selection(self, mock_openai):
        """errortypes_v3 프롬프트 선택 테스트"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = SentenceGenerator(prompt_name="errortypes_v3")

        assert generator.prompt.name == "errortypes_v3"
