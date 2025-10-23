"""
콜론 처리 로직 디버깅 테스트
"""
from src.postprocessors.rule_checklist import RuleChecklistPostprocessor

# 후처리 객체 생성
processor = RuleChecklistPostprocessor()

# 실제 파일에서 발견된 3개 케이스
test_cases = [
    {
        "id": "grm924197",
        "original": "갑자기 침대에서 일어나자 순간적으로 심한 어지러움을 느꼈다. 빈혈 증세일 수 있으니 연세대학교 병원에 가서 정확한 진단을 받아봐야겠다.",
        "corrected": "갑자기 침대에서 일어나자 순간적으로 심한 어지러움을 느꼈다. 빈혈 증세일 수 있으니 연세대학교 병원에 가서 정확한 진단을 받아봐야겠다. : 갑자기 침대에서 일어나자 순간적으로 심한 어지러움을 느꼈다. 빈혈 증상일 수 있으니 연세대학교 병원에 가서 정확한 진단을 받아 봐야겠다."
    },
    {
        "id": "grm780698",
        "original": "내 프로필상 키는 170이지만 실제로는 조금 더 작다.",
        "corrected": "내 프로필상 키는 170이지만 실제로는 조금 더 작다. : 내 프로필상 키는 170이지만 실제로는 조금 더 작다. (규칙에 따라 설명 없이 교정문만 출력합니다.)"
    },
    {
        "id": "grm722124",
        "original": "졸업식이 끝난 후, 명동의 음식점에서 간단한 뒷풀이가 진행되었다.",
        "corrected": "졸업식이 끝난 후, 명동의 음식점에서 간단한 뒷풀이가 진행되었다. : 다만, 지시사항에 따라 원문의 의미를 변경하지 않는 범위에서만 최소한의 교정을 적용했습니다."
    }
]

print("=== 콜론 처리 로직 디버깅 ===\n")

for case in test_cases:
    print(f"ID: {case['id']}")
    print(f"원문: {case['original']}")
    print(f"모델 응답 (Before): {case['corrected']}")

    # Rule-Checklist 적용
    result = processor.process(case['original'], case['corrected'])

    print(f"후처리 결과 (After): {result}")
    print(f"콜론 포함 여부: {' : ' in result or ' ：' in result}")
    print("-" * 80)
