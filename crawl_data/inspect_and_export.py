# inspect_and_export.py
"""
Inspect the labeled LLM PR dataset and export to CSV.

Usage:
    python inspect_and_export.py llm_pr_labeled.jsonl llm_pr_labeled.csv
"""

import sys
import json
import pandas as pd


def load_jsonl_to_df(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                rows.append(obj)
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(rows)


def main():
    if len(sys.argv) < 3:
        print("Usage: python inspect_and_export.py input.jsonl output.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Loading {input_path} ...")
    df = load_jsonl_to_df(input_path)

    print("\n=== Basic shape ===")
    print(df.shape)  # (rows, columns)

    print("\n=== Columns ===")
    print(df.columns.tolist())

    # Make sure ChatgptSharing is boolean
    if "ChatgptSharing" in df.columns:
        df["ChatgptSharing"] = df["ChatgptSharing"].astype(bool)

    print("\n=== LLM usage counts (ChatgptSharing) ===")
    print(df["ChatgptSharing"].value_counts(dropna=False))

    if "RepoName" in df.columns:
        print("\n=== LLM-flagged PRs per Repo ===")
        print(
            df[df["ChatgptSharing"] == True]["RepoName"]
            .value_counts()
            .head(10)
        )

    if "RepoLanguage" in df.columns:
        print("\n=== LLM-flagged PRs per Language ===")
        print(
            df[df["ChatgptSharing"] == True]["RepoLanguage"]
            .value_counts()
            .head(10)
        )

    # Export to CSV
    print(f"\nExporting to CSV: {output_path}")
    df.to_csv(output_path, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
