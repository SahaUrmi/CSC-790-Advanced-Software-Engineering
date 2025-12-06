# add_llm_flags.py
"""
Attach LLM usage flags (ChatgptSharing) to a raw PR JSONL file.

Usage:
    python add_llm_flags.py llm_pr_raw.jsonl llm_pr_labeled.jsonl
"""

import sys
import json
from typing import Dict, Any

from llm_heuristics import LLMUsageDetector


def process_file(input_path: str, output_path: str) -> None:
    detector = LLMUsageDetector()

    total = 0
    positives = 0

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue

            try:
                row: Dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                # skip bad lines
                continue

            flag, debug = detector.detect(row)
            row["ChatgptSharing"] = bool(flag)

            # (Optional) if you want to keep debug info, you could:
            # row["_llm_debug"] = debug

            fout.write(json.dumps(row, ensure_ascii=False) + "\n")

            total += 1
            if flag:
                positives += 1

    print(f"Processed {total} rows.")
    print(f"LLM-flagged (ChatgptSharing=True): {positives}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python add_llm_flags.py input_raw.jsonl output_labeled.jsonl")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    process_file(input_path, output_path)


if __name__ == "__main__":
    main()
