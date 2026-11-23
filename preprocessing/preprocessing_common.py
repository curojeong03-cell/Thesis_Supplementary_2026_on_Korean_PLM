"""Write and audit the clean dataset partitions."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory


def verify_disjoint(splits, columns):
    """Raise an error if a value is shared by two partitions."""
    for column in columns:
        seen = set()
        for name, rows in splits.items():
            values = set(rows[column])
            if not seen.isdisjoint(values):
                raise ValueError(f"Partition overlap in {column!r} at {name!r}")
            seen.update(values)


def write_outputs(output, splits, audit):
    """Write into a fresh directory only after all partitions are ready."""
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    audit["partitions"] = {
        name: {
            "rows": len(rows),
            "labels": rows["label_name"].value_counts().sort_index().to_dict(),
        }
        for name, rows in splits.items()
    }
    with TemporaryDirectory(prefix=".preprocessing-", dir=output.parent) as temp:
        staging = Path(temp) / "output"
        staging.mkdir()
        for name, rows in splits.items():
            rows.to_csv(staging / f"{name}.csv", index=False, encoding="utf-8-sig")
        (staging / "preprocessing_report.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if output.exists():
            raise FileExistsError(f"Output directory already exists: {output}")
        staging.rename(output)
    for name, rows in splits.items():
        print(f"{name:5s} {len(rows):>7,d}")
    print(f"Saved to {output}")
