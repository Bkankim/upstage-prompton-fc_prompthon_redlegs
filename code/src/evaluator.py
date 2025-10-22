"""
평가 실행 클래스
정답 데이터와 예측 데이터를 비교하여 평가 수행
"""

import pandas as pd
from typing import Dict

from src.metrics.evaluator import evaluate_correction


class Evaluator:
    """
    교정 결과 평가기 클래스
    정답과 예측을 비교하여 Recall, Precision 계산
    """

    def __init__(self):
        """평가기 초기화"""
        pass

    def evaluate(self, true_df: pd.DataFrame, pred_df: pd.DataFrame) -> Dict:
        """교정 결과 평가 수행"""
        
        # 필수 컬럼 검증
        if not {"err_sentence", "cor_sentence"}.issubset(true_df.columns):
            raise ValueError(
                f"Truth DF must have columns 'err_sentence' and 'cor_sentence' (found: {list(true_df.columns)})"
            )

        if "cor_sentence" not in pred_df.columns:
            raise ValueError(
                f"Prediction DF must have column 'cor_sentence' (found: {list(pred_df.columns)})"
            )

        # 데이터 길이 검증
        if len(true_df) != len(pred_df):
            raise ValueError(
                f"Length mismatch: truth={len(true_df)} vs pred={len(pred_df)}. Ensure one-to-one rows."
            )

        # err_sentence 순서 검증 (있는 경우)
        if "err_sentence" in pred_df.columns:
            if not true_df["err_sentence"].astype(str).equals(pred_df["err_sentence"].astype(str)):
                raise ValueError(
                    "Row order/content mismatch in 'err_sentence' between truth and submission."
                )

        # 예측 데이터 정규화 (cor_sentence만 사용)
        pred_df_normalized = pd.DataFrame({"cor_sentence": pred_df["cor_sentence"].astype(str)})

        # 평가 수행
        results = evaluate_correction(true_df, pred_df_normalized)

        # 추가 컬럼이 있으면 분석 결과에 포함
        if "original_target_part" in true_df.columns and "golden_target_part" in true_df.columns:
            results['analysis_df']['original_target_part'] = true_df['original_target_part'].values
            results['analysis_df']['golden_target_part'] = true_df['golden_target_part'].values

        return results
