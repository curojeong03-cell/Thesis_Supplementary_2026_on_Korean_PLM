"""Create small, synthetic inputs that exercise both preprocessing scripts."""

import argparse
import csv
import json
from pathlib import Path


CATEGORIES = ("IT과학", "역사", "생활건강", "사회", "문화", "금융")


def make_aihub(root):
    for partition, sequence_start in (("Training", 0), ("Validation", 12)):
        label_dir = root / "aihub" / partition / "02.라벨링데이터"
        label_dir.mkdir(parents=True)
        for category in CATEGORIES:
            for sequence in range(sequence_start, sequence_start + 12):
                document_id = f"{category}-{sequence:02d}"
                document = {
                    "metaData": {"ID": document_id, "CATEGORY": category, "MEDIA_TYPE": "합성 문서"},
                    "annotation": [
                        {
                            "text": f"{category} 예제 문서 {sequence:02d}번 첫 번째 문장입니다.",
                            "label": "사실형",
                            "value": {"word_num": 7},
                        },
                        {
                            "text": f"{category} 예제 문서 {sequence:02d}번 두 번째 문장입니다.",
                            "label": "추론형",
                            "value": {"word_num": 7},
                        },
                    ],
                }
                (label_dir / f"{document_id}.json").write_text(
                    json.dumps(document, ensure_ascii=False), encoding="utf-8",
                )


def write_reviews(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(("id", "document", "label"))
        writer.writerows(rows)


def make_nsmc(root):
    directory = root / "nsmc"
    directory.mkdir()
    train = [
        (i, f"가상 훈련 자료에서 만든 예시 리뷰 {i:02d}번입니다.", i % 2)
        for i in range(100)
    ]
    test = [
        (i, f"가상 평가 자료에서 만든 예시 리뷰 {i:02d}번입니다.", i % 2)
        for i in range(100, 124)
    ]
    train.extend([
        (200, "가상 훈련 자료에 반복 자모가 있네요ㅋㅋㅋ!!!", 1),
        (201, "가상 훈련 자료에 반복 자모가 있네요ㅋㅋ!!", 1),
        (202, "이 예시 리뷰에는 서로 다른 레이블이 붙습니다.", 0),
        (203, "이 예시 리뷰에는 서로 다른 레이블이 붙습니다.", 1),
        (204, test[0][1], test[0][2]),
        (205, "짧은 문장", 1),
        (206, "이 리뷰의 예시 레이블은 분류 범위 밖입니다.", 9),
    ])
    write_reviews(directory / "ratings_train.txt", train)
    write_reviews(directory / "ratings_test.txt", test)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New directory for the synthetic inputs")
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    make_aihub(args.output)
    make_nsmc(args.output)
    print(f"Synthetic inputs saved to {args.output}")


if __name__ == "__main__":
    main()
