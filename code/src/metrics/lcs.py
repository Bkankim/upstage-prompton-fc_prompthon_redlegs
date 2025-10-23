"""
최장 공통 부분수열(LCS) 기반 텍스트 차이점 검출 모듈
"""

import pandas as pd
from typing import List, Tuple


def tokenize(text: str) -> List[str]:
    """텍스트를 토큰으로 분리"""
    if pd.isna(text):
        return []
    return str(text).split()


def lcs_table(X: List[str], Y: List[str]) -> List[List[int]]:
    """최장 공통 부분수열(LCS) 테이블 생성"""
    m = len(X)
    n = len(Y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])
    return L


def find_lcs(X: List[str], Y: List[str]) -> List[str]:
    """최장 공통 부분수열(LCS) 찾기"""
    L = lcs_table(X, Y)
    i = len(X)
    j = len(Y)
    lcs = []
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            i -= 1
            j -= 1
        elif L[i-1][j] > L[i][j-1]:
            i -= 1
        else:
            j -= 1
    return lcs[::-1]


def find_differences_with_offsets(original: str, corrected: str) -> List[Tuple[str, str, int, int, int, int]]:
    """원문과 교정문 간의 차이점 찾기"""
    original_tokens = tokenize(original)
    corrected_tokens = tokenize(corrected)
    lcs = find_lcs(original_tokens, corrected_tokens)
    
    orig_index = 0
    corr_index = 0
    lcs_index = 0
    differences = []
    
    while orig_index < len(original_tokens) or corr_index < len(corrected_tokens):
        orig_diff = []
        corr_diff = []
        orig_start = orig_index
        corr_start = corr_index
        
        while orig_index < len(original_tokens) and (lcs_index >= len(lcs) or original_tokens[orig_index] != lcs[lcs_index]):
            orig_diff.append(original_tokens[orig_index])
            orig_index += 1
        while corr_index < len(corrected_tokens) and (lcs_index >= len(lcs) or corrected_tokens[corr_index] != lcs[lcs_index]):
            corr_diff.append(corrected_tokens[corr_index])
            corr_index += 1
            
        if orig_diff or corr_diff:
            differences.append((' '.join(orig_diff), ' '.join(corr_diff), orig_start, orig_index, corr_start, corr_index))
        if lcs_index < len(lcs):
            lcs_index += 1
            orig_index += 1
            corr_index += 1
            
    # 근접한 차이점 병합
    new_differences = []
    for i, d in enumerate(differences):
        if i == 0:
            new_differences.append(d)
            continue
        if d[2] - differences[i-1][2] <= 2:
            new_differences[-1] = (
                new_differences[-1][0] + ' ' + d[0],
                new_differences[-1][1] + ' ' + d[1],
                new_differences[-1][2], d[3],
                new_differences[-1][4], d[5]
            )
        else:
            new_differences.append(d)
            
    return new_differences
