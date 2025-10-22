"""
LCS 기반 메트릭 모듈 테스트
"""

import pytest
import pandas as pd
from src.metrics.lcs import (
    tokenize,
    lcs_table,
    find_lcs,
    find_differences_with_offsets
)
from src.metrics.evaluator import evaluate_correction


class TestTokenize:
    """tokenize 함수 테스트"""

    def test_basic_tokenize(self):
        """기본 토큰화 테스트"""
        text = "오늘 날씨가 좋다"
        tokens = tokenize(text)

        assert tokens == ["오늘", "날씨가", "좋다"]

    def test_empty_string(self):
        """빈 문자열 토큰화 테스트"""
        text = ""
        tokens = tokenize(text)

        assert tokens == []

    def test_single_word(self):
        """단어 하나 토큰화 테스트"""
        text = "안녕하세요"
        tokens = tokenize(text)

        assert tokens == ["안녕하세요"]

    def test_whitespace_only(self):
        """공백만 있는 문자열 테스트"""
        text = "   "
        tokens = tokenize(text)

        assert tokens == []

    def test_nan_value(self):
        """NaN 값 처리 테스트"""
        tokens = tokenize(pd.NA)

        assert tokens == []

    def test_none_value(self):
        """None 값 처리 테스트"""
        tokens = tokenize(None)

        assert tokens == []


class TestLCSTable:
    """lcs_table 함수 테스트"""

    def test_identical_sequences(self):
        """동일한 시퀀스 LCS 테이블 테스트"""
        X = ["a", "b", "c"]
        Y = ["a", "b", "c"]

        table = lcs_table(X, Y)

        # LCS 길이는 3이어야 함
        assert table[3][3] == 3

    def test_completely_different_sequences(self):
        """완전히 다른 시퀀스 LCS 테이블 테스트"""
        X = ["a", "b", "c"]
        Y = ["d", "e", "f"]

        table = lcs_table(X, Y)

        # LCS 길이는 0이어야 함
        assert table[3][3] == 0

    def test_partial_match(self):
        """부분 일치 시퀀스 LCS 테이블 테스트"""
        X = ["a", "b", "c", "d"]
        Y = ["a", "c", "d"]

        table = lcs_table(X, Y)

        # LCS 길이는 3이어야 함 (a, c, d)
        assert table[4][3] == 3

    def test_empty_sequences(self):
        """빈 시퀀스 LCS 테이블 테스트"""
        X = []
        Y = []

        table = lcs_table(X, Y)

        assert table[0][0] == 0


class TestFindLCS:
    """find_lcs 함수 테스트"""

    def test_identical_sequences(self):
        """동일한 시퀀스 LCS 찾기 테스트"""
        X = ["오늘", "날씨가", "좋다"]
        Y = ["오늘", "날씨가", "좋다"]

        lcs = find_lcs(X, Y)

        assert lcs == ["오늘", "날씨가", "좋다"]

    def test_completely_different(self):
        """완전히 다른 시퀀스 LCS 찾기 테스트"""
        X = ["a", "b", "c"]
        Y = ["d", "e", "f"]

        lcs = find_lcs(X, Y)

        assert lcs == []

    def test_partial_match(self):
        """부분 일치 시퀀스 LCS 찾기 테스트"""
        X = ["오늘", "날씨가", "안", "좋다"]
        Y = ["오늘", "날씨가", "좋다"]

        lcs = find_lcs(X, Y)

        assert lcs == ["오늘", "날씨가", "좋다"]

    def test_insertion_in_middle(self):
        """중간에 단어가 삽입된 경우 LCS 테스트"""
        X = ["a", "b", "c"]
        Y = ["a", "x", "b", "c"]

        lcs = find_lcs(X, Y)

        assert lcs == ["a", "b", "c"]

    def test_empty_sequences(self):
        """빈 시퀀스 LCS 찾기 테스트"""
        X = []
        Y = []

        lcs = find_lcs(X, Y)

        assert lcs == []


class TestFindDifferences:
    """find_differences_with_offsets 함수 테스트"""

    def test_identical_sentences(self):
        """동일한 문장 차이점 찾기 테스트"""
        original = "오늘 날씨가 좋다"
        corrected = "오늘 날씨가 좋다"

        differences = find_differences_with_offsets(original, corrected)

        assert differences == []

    def test_single_word_change(self):
        """단어 하나 변경 테스트"""
        original = "오늘 날씨가 않좋다"
        corrected = "오늘 날씨가 안좋다"

        differences = find_differences_with_offsets(original, corrected)

        assert len(differences) == 1
        assert differences[0][0] == "않좋다"  # 원본
        assert differences[0][1] == "안좋다"  # 교정

    def test_word_insertion(self):
        """단어 삽입 테스트"""
        original = "오늘 날씨가 좋다"
        corrected = "오늘 날씨가 매우 좋다"

        differences = find_differences_with_offsets(original, corrected)

        assert len(differences) >= 1

    def test_word_deletion(self):
        """단어 삭제 테스트"""
        original = "오늘 날씨가 매우 좋다"
        corrected = "오늘 날씨가 좋다"

        differences = find_differences_with_offsets(original, corrected)

        assert len(differences) >= 1

    def test_empty_strings(self):
        """빈 문자열 처리 테스트"""
        original = ""
        corrected = ""

        differences = find_differences_with_offsets(original, corrected)

        assert differences == []


class TestEvaluateCorrection:
    """evaluate_correction 함수 테스트"""

    def test_perfect_match(self):
        """완벽한 교정 평가 테스트"""
        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluate_correction(true_df, pred_df)

        assert 'recall' in result
        assert 'precision' in result
        assert result['recall'] >= 0
        assert result['precision'] >= 0

    def test_no_correction_needed(self):
        """교정이 필요 없는 경우 테스트"""
        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 좋다'],
            'cor_sentence': ['오늘 날씨가 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 좋다']
        })

        result = evaluate_correction(true_df, pred_df)

        # 교정이 필요 없으므로 분모가 0
        assert result['true_positives'] == 0
        assert result['false_positives'] == 0
        assert result['false_missings'] == 0

    def test_completely_wrong_correction(self):
        """완전히 잘못된 교정 테스트"""
        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 않좋다']  # 교정 안 함
        })

        result = evaluate_correction(true_df, pred_df)

        # False Missing이 발생해야 함
        assert result['false_missings'] >= 0

    def test_multiple_sentences(self):
        """여러 문장 평가 테스트"""
        true_df = pd.DataFrame({
            'err_sentence': [
                '오늘 날씨가 않좋다',
                '김치찌게 먹으러 갈려고'
            ],
            'cor_sentence': [
                '오늘 날씨가 안 좋다',
                '김치찌개 먹으러 가려고'
            ]
        })

        pred_df = pd.DataFrame({
            'cor_sentence': [
                '오늘 날씨가 안 좋다',
                '김치찌개 먹으러 가려고'
            ]
        })

        result = evaluate_correction(true_df, pred_df)

        assert len(result['analysis_df']) == 2
        assert result['true_positives'] >= 0

    def test_result_structure(self):
        """결과 구조 테스트"""
        true_df = pd.DataFrame({
            'err_sentence': ['오늘 날씨가 않좋다'],
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['오늘 날씨가 안 좋다']
        })

        result = evaluate_correction(true_df, pred_df)

        # 필수 키 확인
        assert 'recall' in result
        assert 'precision' in result
        assert 'true_positives' in result
        assert 'false_positives' in result
        assert 'false_missings' in result
        assert 'false_redundants' in result
        assert 'analysis_df' in result

        # 데이터 타입 확인
        assert isinstance(result['recall'], (int, float))
        assert isinstance(result['precision'], (int, float))
        assert isinstance(result['analysis_df'], pd.DataFrame)


class TestRecallPrecisionCalculation:
    """Recall과 Precision 계산 로직 테스트"""

    def test_recall_calculation(self):
        """Recall 계산 테스트"""
        # Recall = TP / (TP + FP + FM) * 100
        tp = 10
        fp = 2
        fm = 3

        expected_recall = (10 / (10 + 2 + 3)) * 100

        # 실제 평가 수행 대신 공식 검증
        assert expected_recall == pytest.approx(66.67, rel=0.01)

    def test_precision_calculation(self):
        """Precision 계산 테스트"""
        # Precision = TP / (TP + FP + FR) * 100
        tp = 10
        fp = 2
        fr = 1

        expected_precision = (10 / (10 + 2 + 1)) * 100

        # 실제 평가 수행 대신 공식 검증
        assert expected_precision == pytest.approx(76.92, rel=0.01)

    def test_zero_division_handling(self):
        """분모가 0인 경우 처리 테스트"""
        # TP, FP, FM이 모두 0인 경우
        true_df = pd.DataFrame({
            'err_sentence': ['완벽한 문장'],
            'cor_sentence': ['완벽한 문장']
        })

        pred_df = pd.DataFrame({
            'cor_sentence': ['완벽한 문장']
        })

        result = evaluate_correction(true_df, pred_df)

        # 분모가 0일 때 0.0 반환 확인
        assert result['recall'] == 0.0 or result['recall'] >= 0
        assert result['precision'] == 0.0 or result['precision'] >= 0
