import os
import argparse

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
from prompts import errortypes_v3_prompt

# Load environment variables
load_dotenv()

def main():
    """
    Error Types v3 프롬프트를 사용하여 문장 교정 수행
    10가지 오류 유형 체크리스트 방식으로 검토
    """
    parser = argparse.ArgumentParser(description="Generate corrected sentences using Error Types v3 prompt")
    parser.add_argument("--input", default="data/train_dataset.csv", help="Input CSV path containing err_sentence column")
    parser.add_argument("--output", default="submission_errortypes_v3.csv", help="Output CSV path")
    parser.add_argument("--model", default="solar-pro2", help="Model name (default: solar-pro2)")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.input)

    if "err_sentence" not in df.columns:
        raise ValueError("Input CSV must contain 'err_sentence' column")

    # Setup Upstage client
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")

    print(f"Prompt: Error Types v3 (10-item checklist)")
    print(f"Model: {args.model}")
    print(f"Output: {args.output}")

    err_sentences = []
    cor_sentences = []

    # Process each sentence
    for text in tqdm(df["err_sentence"].astype(str).tolist(), desc="Generating"):
        err_sentences.append(text)

        try:
            prompt = errortypes_v3_prompt.format(text=text)
            resp = client.chat.completions.create(
                model=args.model,
                messages=[
                    {"role": "system", "content": "당신은 한국어 문장 교정 전문가입니다. 체크리스트를 따라 모든 오류 유형을 꼼꼼히 검토하세요. 반드시 불필요한 설명 없이 교정된 문장만 출력하세요."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            corrected = resp.choices[0].message.content.strip()
            cor_sentences.append(corrected)

        except Exception as e:
            print(f"Error processing: {text[:50]}... - {e}")
            cor_sentences.append(text)  # fallback to original

    # Save results with required column names
    out_df = pd.DataFrame({"err_sentence": err_sentences, "cor_sentence": cor_sentences})
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {len(out_df)} rows to {args.output}")


if __name__ == "__main__":
    main()
