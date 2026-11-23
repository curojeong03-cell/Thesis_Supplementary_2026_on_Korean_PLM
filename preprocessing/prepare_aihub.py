"""Prepare the AI-Hub sentence-type corpus for six-topic classification."""

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold

from preprocessing_common import verify_disjoint, write_outputs


LABELS = ("IT과학", "역사", "생활건강", "사회", "문화", "금융")
LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}
SEED = 42
COLUMNS = ("text", "category", "doc_id", "media_type", "word_num", "text_char_len")


def string_or_empty(value):
    return "" if value is None else str(value)


def int_or_missing(value):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def flatten_document(path):
    with path.open(encoding="utf-8-sig") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("JSON document must contain an object")
    metadata = document.get("metaData", {})
    if not isinstance(metadata, dict):
        raise ValueError("metaData must contain an object")
    annotations = document.get("annotation", [])
    if isinstance(annotations, dict):
        annotations = [annotations]
    if not isinstance(annotations, list):
        raise ValueError("annotation must contain a list or an object")

    rows = []
    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        text = string_or_empty(annotation.get("text")).strip()
        if not text:
            continue
        properties = annotation.get("value", {})
        word_num = properties.get("word_num") if isinstance(properties, dict) else None
        rows.append({
            "text": text,
            "category": string_or_empty(metadata.get("CATEGORY")),
            "doc_id": string_or_empty(metadata.get("ID")),
            "media_type": string_or_empty(metadata.get("MEDIA_TYPE")),
            "word_num": int_or_missing(word_num),
            "text_char_len": len(text),
        })
    return rows


def load_annotation_dirs(training, validation):
    rows = []
    partitions = {}
    for name, directory in (("Training", training), ("Validation", validation)):
        if not directory.is_dir():
            raise FileNotFoundError(f"Annotation directory not found: {directory}")
        paths = sorted(
            (path for path in directory.rglob("*.json") if path.suffix == ".json"),
            key=lambda path: path.relative_to(directory).parts,
        )
        if not paths:
            raise ValueError(f"No JSON files in {directory}")
        before = len(rows)
        for path in paths:
            try:
                rows.extend(flatten_document(path))
            except (OSError, ValueError) as exc:
                relative_path = path.relative_to(directory)
                raise ValueError(f"Could not read {name}/{relative_path}: {exc}") from exc
        partitions[name] = {"json_files": len(paths), "sentence_rows": len(rows) - before}
    return pd.DataFrame.from_records(rows, columns=COLUMNS), {
        "type": "annotation_json",
        "source_partitions": partitions,
    }


def load_flattened(path):
    if path.suffix.lower() == ".parquet":
        rows = pd.read_parquet(path)
    elif path.suffix.lower() == ".csv":
        rows = pd.read_csv(path)
    else:
        raise ValueError("The flattened input must be a .parquet or .csv file")
    return rows, {"type": "flattened", "file": path.name}


def clean_rows(raw):
    required = {"text", "category", "doc_id"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing AI-Hub columns: {', '.join(sorted(missing))}")

    category = raw["category"].astype(str)
    rows = raw.loc[category.isin(LABEL_TO_ID)].copy()
    rows["category"] = category.loc[rows.index]
    rows["text"] = rows["text"].astype(str).str.strip()
    by_chars = rows.loc[rows["text"].str.len().between(10, 300)]
    word_count = by_chars["word_num"] if "word_num" in by_chars else by_chars["text"].str.split().str.len()
    by_words = by_chars.loc[word_count >= 4]
    unique = by_words.drop_duplicates(subset="text", keep="first").reset_index(drop=True)

    clean = pd.DataFrame({
        "uid": unique.index,
        "text": unique["text"],
        "label_name": unique["category"],
        "label_id": unique["category"].map(LABEL_TO_ID),
        "doc_group": unique["doc_id"].astype(str),
    })
    for column in ("media_type", "word_num", "text_char_len"):
        if column in unique:
            clean[column] = unique[column]
    return clean, {
        "input_rows": len(raw),
        "after_category_filter": len(rows),
        "after_character_filter": len(by_chars),
        "after_word_filter": len(by_words),
        "after_text_deduplication": len(clean),
        "document_groups": int(clean["doc_group"].nunique()),
    }


def group_split(rows, held_out_ratio):
    groups = rows["doc_group"]
    labels = rows["label_id"]
    folds = round(1 / held_out_ratio)
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=SEED)
    try:
        remaining, held_out = next(splitter.split(rows, labels, groups))
        method = f"StratifiedGroupKFold(n_splits={folds})"
    except ValueError as exc:
        fallback = GroupShuffleSplit(n_splits=1, test_size=held_out_ratio, random_state=SEED)
        remaining, held_out = next(fallback.split(rows, labels, groups))
        method = f"GroupShuffleSplit(test_size={held_out_ratio})"
        print(f"Using {method}: {exc}")
    return rows.iloc[remaining], rows.iloc[held_out], method


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--training-labels", type=Path, help="Training label JSON directory")
    source.add_argument("--flattened", type=Path, help="Existing AI-Hub Parquet or CSV file")
    parser.add_argument("--validation-labels", type=Path, help="Validation label JSON directory")
    parser.add_argument("--output", type=Path, required=True, help="New directory for the outputs")
    args = parser.parse_args()
    if args.training_labels is not None and args.validation_labels is None:
        parser.error("--training-labels requires --validation-labels")
    if args.flattened is not None and args.validation_labels is not None:
        parser.error("--validation-labels is used with --training-labels")

    if args.flattened is not None:
        raw, input_audit = load_flattened(args.flattened)
    else:
        raw, input_audit = load_annotation_dirs(args.training_labels, args.validation_labels)
    clean, row_audit = clean_rows(raw)
    remaining, test, test_method = group_split(clean, 0.20)
    train, valid, validation_method = group_split(remaining, 0.10)
    splits = {"train": train, "valid": valid, "test": test}
    verify_disjoint(splits, ("doc_group", "text"))
    audit = {
        "dataset": "AI-Hub",
        "input": input_audit,
        "row_counts": row_audit,
        "split_seed": SEED,
        "test_method": test_method,
        "validation_method": validation_method,
        "checked_disjoint_columns": ["doc_group", "text"],
    }
    write_outputs(args.output, splits, audit)


if __name__ == "__main__":
    main()
