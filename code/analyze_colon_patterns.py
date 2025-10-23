"""
콜론 패턴 심층 분석
"""
import pandas as pd
import re

# 현재 버전 (Response Cleaning만)의 원본 응답 재현
# Test 데이터로 다시 생성해서 분석

print("=== 콜론 패턴 분석 ===\n")

# 알려진 문제 케이스 직접 분석
problem_cases = [
    {
        "id": "grm938521",
        "original": "대학입학 전형에서 서울대의 수시 비중은 7:3이었다.",
        "description": "비율 표기 콜론"
    },
    {
        "id": "grm176588",
        "original": "먼 훗날의 역사가는 21세기형 죽음을 어떻게 기술하게 될까?",
        "description": "인용문 내 콜론"
    }
]

# 가능한 콜론 패턴 분류
patterns = {
    "ratio": r'\d+\s*:\s*\d+',  # 비율 (7:3, 1:2 등)
    "time": r'\d{1,2}:\d{2}',   # 시간 (3:00, 10:30 등)
    "metadata": r'[가-힣\s]+\s*:\s*[가-힣\s]+',  # 원문 : 교정문
    "quote": r'["""][^"""]*:[^"""]*["""]',  # 인용문 내 콜론
}

print("=== 콜론 패턴 유형 ===")
print("1. 비율 표기: 7:3, 3:2, 1:1 등")
print("2. 시간 표기: 3:00, 10:30 등")
print("3. 메타데이터: '원문 : 교정문' 형식")
print("4. 인용문 내: \"사람에겐 얼마만큼의 땅이 필요한가?\"")

print("\n=== 문제 케이스 분석 ===\n")

# grm938521 케이스 시뮬레이션
text = "대학 입학 전형에서 서울대의 수시 비중은 7:3이었다."
print(f"케이스: grm938521")
print(f"원문: {text}")
print(f"콜론 포함: {':' in text}")

if ':' in text:
    parts = re.split(r'\s*:\s*', text, maxsplit=1)
    print(f"분리 결과: {parts}")
    print(f"현재 로직 적용 시: '{parts[1]}'")
    print(f"→ 문제: '7:3'의 콜론을 메타데이터로 오인!\n")

# 해결책 제안
print("=== 해결책 분석 ===\n")

# 방법 1: 비율/시간 패턴 먼저 체크
print("방법 1: 비율/시간 패턴 제외")
if re.search(r'\d+\s*:\s*\d+', text):
    print(f"비율 패턴 발견: {re.findall(r'\d+\s*:\s*\d+', text)}")
    print("→ 콜론 분리 스킵")

# 방법 2: 메타데이터 패턴 정교화
print("\n방법 2: 메타데이터 패턴 정교화")
metadata_pattern = r'^([^:]+)\s*:\s*(.+)$'
print(f"패턴: {metadata_pattern}")
print("조건:")
print("  - 문장 시작부터 콜론까지가 한글 위주")
print("  - '원문', '교정', '수정' 등의 키워드 포함")

# 방법 3: 위치 기반 판단
print("\n방법 3: 위치 기반 판단")
print("콜론이 문장 앞부분(25% 이내)에 있고")
print("앞부분이 '원문', '교정문', '수정' 등의 단어를 포함하면 메타데이터")

# 최적 로직 제안
print("\n=== 최적 로직 제안 ===")
print("""
def is_metadata_colon(text):
    # 1. 비율/시간 패턴이 있으면 정상 콜론
    if re.search(r'\\d+\\s*:\\s*\\d+', text):
        return False

    # 2. 콜론이 문장 앞부분(30% 이내)에만 있고
    #    앞부분에 메타데이터 키워드가 있으면 메타데이터
    colon_pos = text.find(':')
    if colon_pos > 0 and colon_pos / len(text) < 0.3:
        before_colon = text[:colon_pos].strip()
        keywords = ['원문', '교정', '수정', '결과', '답변']
        if any(kw in before_colon for kw in keywords):
            return True

    return False
""")

# 테스트
test_cases = [
    "대학 입학 전형에서 서울대의 수시 비중은 7:3이었다.",  # 비율
    "원문 : 교정된 문장입니다.",  # 메타데이터
    "교정: 수정된 내용",  # 메타데이터
    "회의 시간은 오후 3:30입니다.",  # 시간
]

def is_metadata_colon(text):
    # 비율/시간 패턴 체크
    if re.search(r'\d+\s*:\s*\d+', text):
        return False

    # 메타데이터 패턴 체크
    colon_pos = text.find(':')
    if colon_pos > 0 and colon_pos / len(text) < 0.3:
        before_colon = text[:colon_pos].strip()
        keywords = ['원문', '교정', '수정', '결과', '답변', '정답']
        if any(kw in before_colon for kw in keywords):
            return True

    return False

print("\n=== 제안 로직 테스트 ===\n")
for i, test in enumerate(test_cases, 1):
    result = is_metadata_colon(test)
    print(f"{i}. {test[:50]}...")
    print(f"   메타데이터: {result}")
    print(f"   → {'콜론 분리 실행' if result else '콜론 분리 스킵'}\n")
