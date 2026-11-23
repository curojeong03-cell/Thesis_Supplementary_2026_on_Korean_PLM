"""Prepare the official NSMC train and test files for sentiment classification."""

import argparse
import csv
import re
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from preprocessing_common import verify_disjoint, write_outputs


SEED = 42
LABELS = {0: "negative", 1: "positive"}
JAMO_REPEAT = re.compile(r"([ㄱ-ㅎㅏ-ㅣ])\1+")
PUNCTUATION_REPEAT = re.compile(r"([!?.~,])\1+")
WHITESPACE = re.compile(r"\s+")


def read_tsv(path):
    return pd.read_csv(path, sep="\t", quoting=csv.QUOTE_NONE, dtype={"id": str})


def normalize(text):
    text = str(text).replace("\u200b", " ").strip()
    text = JAMO_REPEAT.sub(r"\1\1", text)
    text = PUNCTUATION_REPEAT.sub(r"\1\1", text)
    return WHITESPACE.sub(" ", text).strip()


def clean_file(path):
    raw = read_tsv(path)
    missing = {"id", "document", "label"}.difference(raw.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {', '.join(sorted(missing))}")

    numeric_label = pd.to_numeric(raw["label"], errors="coerce")
    accepted_labels = numeric_label.isin(LABELS)
    rows = raw.loc[accepted_labels, ["id", "document"]].rename(columns={"document": "text"})
    rows["text"] = rows["text"].fillna("").map(normalize)
    rows["label_id"] = numeric_label.loc[rows.index].astype(int)
    rows["label_name"] = rows["label_id"].map(LABELS)

    text = rows["text"]
    by_length = rows.loc[text.str.len().between(6, 300) & (text.str.split().str.len() >= 4)]
    labels_by_text = by_length.groupby("text")["label_id"].nunique()
    conflicting_text = labels_by_text.index[labels_by_text > 1]
    no_conflicts = by_length.loc[~by_length["text"].isin(conflicting_text)]
    unique = no_conflicts.drop_duplicates(subset="text", keep="first").reset_index(drop=True)
    return unique, {
        "input_rows": len(raw),
        "invalid_label_rows_removed": len(raw) - len(rows),
        "length_filter_rows_removed": len(rows) - len(by_length),
        "conflicting_text_groups": len(conflicting_text),
        "conflicting_label_rows_removed": len(by_length) - len(no_conflicts),
        "same_label_duplicate_rows_removed": len(no_conflicts) - len(unique),
        "after_within_file_cleaning": len(unique),
    }


def check_combined_ids(combined_path, train_path, test_path):
    combined = read_tsv(combined_path)
    train_ids = set(read_tsv(train_path)["id"])
    test_ids = set(read_tsv(test_path)["id"])
    return {
        "rows": len(combined),
        "ids_match_official_train_test_union": set(combined["id"]) == train_ids | test_ids,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Directory with official NSMC files")
    parser.add_argument("--output", type=Path, required=True, help="New directory for the outputs")
    args = parser.parse_args()

    train_path = args.input / "ratings_train.txt"
    test_path = args.input / "ratings_test.txt"
    official_train, train_audit = clean_file(train_path)
    test, test_audit = clean_file(test_path)
    overlaps_test = official_train["text"].isin(test["text"])
    remaining_train = official_train.loc[~overlaps_test].reset_index(drop=True)
    train, valid = train_test_split(
        remaining_train, test_size=0.10, random_state=SEED, shuffle=True,
        stratify=remaining_train["label_id"],
    )
    splits = {"train": train.copy(), "valid": valid.copy(), "test": test}
    verify_disjoint(splits, ("text",))
    for name, rows in splits.items():
        rows["uid"] = name + "_" + rows["id"].astype(str)
        if not rows["uid"].is_unique:
            raise ValueError(f"Duplicate review IDs in {name} partition")

    audit = {
        "dataset": "NSMC",
        "input_files": [train_path.name, test_path.name],
        "official_train": train_audit,
        "official_test": test_audit,
        "train_rows_removed_for_test_overlap": int(overlaps_test.sum()),
        "split_seed": SEED,
        "validation_ratio": 0.10,
        "checked_disjoint_columns": ["text"],
    }
    combined_path = args.input / "ratings.txt"
    if combined_path.is_file():
        audit["combined_file_audit"] = check_combined_ids(combined_path, train_path, test_path)
    write_outputs(args.output, splits, audit)


if __name__ == "__main__":
    main()
