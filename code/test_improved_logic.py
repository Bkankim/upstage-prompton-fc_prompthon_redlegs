"""
개선된 콜론 처리 로직 테스트
"""
from src.postprocessors.rule_checklist import RuleChecklistPostprocessor

processor = RuleChecklistPostprocessor()

# 문제 케이스들
test_cases = [
    {
        "id": "grm938521",
        "original": "대학입학 전형에서 서울대의 수시 비중은 7:3이었다.",
        "corrected": "대학 입학 전형에서 서울대의 수시 비중은 7:3이었다.",
        "expected": "대학 입학 전형에서 서울대의 수시 비중은 7:3이었다.",
        "description": "비율 표기 - 콜론 유지"
    },
    {
        "id": "metadata1",
        "original": "원문",
        "corrected": "원문 : 교정된 문장입니다.",
        "expected": "교정된 문장입니다.",
        "description": "메타데이터 - 콜론 분리"
    },
    {
        "id": "metadata2",
        "original": "원문",
        "corrected": "교정: 수정된 내용입니다.",
        "expected": "수정된 내용입니다.",
        "description": "메타데이터 (공백 없음) - 콜론 분리"
    },
    {
        "id": "time",
        "original": "원문",
        "corrected": "회의 시간은 오후 3:30입니다.",
        "expected": "회의 시간은 오후 3:30입니다.",
        "description": "시간 표기 - 콜론 유지"
    },
    {
        "id": "grm924197",
        "original": "갑자기 침대에서 일어나자 순간적으로 심한 어지러움을 느꼈다. 빈혈 증세일 수 있으니 연세대학교 병원에 가서 정확한 진단을 받아봐야겠다.",
        "corrected": "갑자기 침대에서 일어나자 순간적으로 심한 어지러움을 느꼈다. 빈혈 증세일 수 있으니 연세대학교 병원에 가서 정확한 진단을 받아봐야겠다.",
        "expected_pattern": "받아 봐야겠다",  # 문법 규칙 적용
        "description": "보조용언 띄어쓰기"
    }
]

print("=== 개선된 로직 테스트 ===\n")

success_count = 0
for case in test_cases:
    result = processor.process(case["original"], case["corrected"])

    if "expected" in case:
        success = (result == case["expected"])
    else:
        success = (case["expected_pattern"] in result)

    success_count += success

    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} [{case['id']}] {case['description']}")
    print(f"  입력: {case['corrected'][:80]}...")
    print(f"  출력: {result[:80]}...")
    if not success:
        if "expected" in case:
            print(f"  예상: {case['expected'][:80]}...")
        else:
            print(f"  패턴: {case['expected_pattern']}")
    print()

print(f"=== 결과: {success_count}/{len(test_cases)} 성공 ({success_count/len(test_cases)*100:.0f}%) ===")
