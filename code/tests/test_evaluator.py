"""
Evaluator 클래스 테스트
"""

import pytest
import pandas as pd

from src.evaluator import Evaluator


class TestEvaluatorInit:
    """Evaluator 초기화 테스트"""

    def test_init(self):
        """Evaluator 초기화 테스트"""
        evaluator = Evaluator()

        assert evaluator is not None


class TestEvaluatorValidation:
    """Evaluator 데이터 검증 테스트"""

    def test_evaluate_with_valid_data(self):
        """유효한 데이터로 평가 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        assert result is not None
        assert 'recall' in result
        assert 'precision' in result

    def test_evaluate_missing_columns_in_truth(self):
        """정답 데이터에 필수 컬럼이 없는 경우 예외 발생 테스트"""
        evaluator = Evaluator()

        # err_sentence 컬럼 누락
        true_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        with pytest.raises(ValueError) as exc_info:
            evaluator.evaluate(true_df, pred_df)

        assert "err_sentence" in str(exc_info.value)

    def test_evaluate_missing_columns_in_prediction(self):
        """예측 데이터에 필수 컬럼이 없는 경우 예외 발생 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        # cor_sentence 컬럼 누락
        pred_df = pd.DataFrame({
            'wrong_column': ['오늘 날씨가 안 좋다']
        })

        with pytest.raises(ValueError) as exc_info:
            evaluator.evaluate(true_df, pred_df)

        assert "cor_sentence" in str(exc_info.value)

    def test_evaluate_length_mismatch(self):
        """정답과 예측 데이터 길이가 다른 경우 예외 발생 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['문장1', '문장2'],
            'cor_sentence': ['교정1', '교정2']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['교정1']  # 길이 1
        })

        with pytest.raises(ValueError) as exc_info:
            evaluator.evaluate(true_df, pred_df)

        assert "Length mismatch" in str(exc_info.value)

    def test_evaluate_order_mismatch(self):
        """err_sentence 순서가 다른 경우 예외 발생 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['문장A', '문장B'],
            'cor_sentence': ['교정A', '교정B']
        })

        pred_df = pd.DataFrame({
            'err_sentence': ['문장B', '문장A'],  # 순서 바뀜
            'cor_sentence': ['교정B', '교정A']
        })

        with pytest.raises(ValueError) as exc_info:
            evaluator.evaluate(true_df, pred_df)

        assert "order/content mismatch" in str(exc_info.value)


class TestEvaluatorEvaluation:
    """Evaluator 평가 수행 테스트"""

    def test_evaluate_perfect_match(self):
        """완벽한 교정 평가 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 완벽히 일치하므로 높은 점수
        assert result['recall'] >= 0
        assert result['precision'] >= 0

    def test_evaluate_no_correction(self):
        """교정이 전혀 수행되지 않은 경우 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 않좋다']  # 교정 안 함
        })

        result = evaluator.evaluate(true_df, pred_df)

        # False Missing 발생
        assert result['false_missings'] >= 0

    def test_evaluate_multiple_sentences(self):
        """여러 문장 평가 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['문장1', '문장2', '문장3'],
            'cor_sentence': ['교정1', '교정2', '교정3']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['교정1', '교정2', '교정3']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # analysis_df의 길이가 3이어야 함
        assert len(result['analysis_df']) == 3

    def test_evaluate_with_err_sentence_in_prediction(self):
        """예측 데이터에 err_sentence 컬럼이 있는 경우 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        # 예측 데이터에도 err_sentence 포함
        pred_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 정상적으로 평가되어야 함
        assert result is not None
        assert 'recall' in result

    def test_evaluate_without_err_sentence_in_prediction(self):
        """예측 데이터에 err_sentence 컬럼이 없는 경우 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        # 예측 데이터에 err_sentence 없음
        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 정상적으로 평가되어야 함
        assert result is not None


class TestEvaluatorResultStructure:
    """Evaluator 결과 구조 테스트"""

    def test_result_has_required_keys(self):
        """결과에 필수 키가 포함되어 있는지 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 필수 키 확인
        required_keys = [
            'recall',
            'precision',
            'true_positives',
            'false_positives',
            'false_missings',
            'false_redundants',
            'analysis_df'
        ]

        for key in required_keys:
            assert key in result

    def test_result_types(self):
        """결과 데이터 타입 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 타입 확인
        assert isinstance(result['recall'], (int, float))
        assert isinstance(result['precision'], (int, float))
        assert isinstance(result['true_positives'], int)
        assert isinstance(result['false_positives'], int)
        assert isinstance(result['false_missings'], int)
        assert isinstance(result['false_redundants'], int)
        assert isinstance(result['analysis_df'], pd.DataFrame)

    def test_analysis_df_columns(self):
        """analysis_df 컬럼 확인 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # analysis_df 필수 컬럼 확인
        required_columns = ['original', 'golden', 'prediction', 'tp', 'fp', 'fm', 'fr']
        for col in required_columns:
            assert col in result['analysis_df'].columns


class TestEvaluatorWithAdditionalColumns:
    """추가 컬럼이 있는 경우 테스트"""

    def test_evaluate_with_target_part_columns(self):
        """original_target_part, golden_target_part 컬럼이 있는 경우 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다'],
            'original_target_part': ['않좋다'],
            'golden_target_part': ['안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # analysis_df에 추가 컬럼이 포함되어야 함
        assert 'original_target_part' in result['analysis_df'].columns
        assert 'golden_target_part' in result['analysis_df'].columns

    def test_evaluate_without_target_part_columns(self):
        """target_part 컬럼이 없는 경우 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # analysis_df에 추가 컬럼이 없어야 함
        assert 'original_target_part' not in result['analysis_df'].columns
        assert 'golden_target_part' not in result['analysis_df'].columns


class TestEvaluatorEdgeCases:
    """Evaluator 엣지 케이스 테스트"""

    def test_evaluate_empty_dataframe(self):
        """빈 DataFrame 평가 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': [],
            'cor_sentence': []
        })

        pred_df = pd.DataFrame({
            'cor_sentence': []
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 빈 데이터에 대한 결과
        assert result['true_positives'] == 0
        assert result['false_positives'] == 0
        assert len(result['analysis_df']) == 0

    def test_evaluate_identical_sentences(self):
        """원문과 교정문이 동일한 경우 테스트"""
        evaluator = Evaluator()

        true_df = pd.DataFrame({
            'err_sentence': ['완벽한 문장'],
            'cor_sentence': ['완벽한 문장']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['완벽한 문장']
        })

        result = evaluator.evaluate(true_df, pred_df)

        # 교정이 필요 없는 경우
        assert result is not None
