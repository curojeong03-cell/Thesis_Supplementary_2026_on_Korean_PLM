# 한국어 분류 데이터 전처리

논문 보조자료. AI-Hub 「문장 유형(추론, 예측 등) 판단 데이터」와 NSMC(Naver Sentiment Movie Corpus)를 학습·검증·평가용 데이터로 구성하는 코드입니다.

## 설치

Python 3.12에서 검증했습니다.

```sh
python -m pip install -r requirements.txt
```

## AI-Hub

[AI-Hub 데이터셋 페이지](https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&dataSetSn=71486&topMenu=100)에서 받은 학습용·검증용 **라벨링 데이터**를 각각 풀어 JSON 폴더를 지정합니다. 배포 데이터의 이용 조건은 [AI-Hub 데이터 이용정책](https://aihub.or.kr/intrcn/guid/usagepolicy.do)에서 확인할 수 있습니다.

```sh
python prepare_aihub.py --training-labels "data/aihub/Training/02.라벨링데이터" --validation-labels "data/aihub/Validation/02.라벨링데이터" --output out/aihub
```

1. 학습용, 검증용 순서로 각 폴더의 JSON을 상대 경로순으로 읽습니다. 문서의 `metaData`와 문장별 `annotation`을 읽어 문장당 한 행을 만들고, 빈 문장을 제거합니다. 읽을 수 없는 JSON이 있으면 해당 입력을 표시하고 중단합니다.
2. 문서의 주제 범주인 `category`를 분류 레이블로 사용합니다. 레이블 ID 0~5는 각각 IT과학, 역사, 생활건강, 사회, 문화, 금융에 대응합니다. JSON의 `annotation.label`은 사실형·추론형 등 문장 유형을 뜻합니다.
3. 양끝 공백을 제거한 텍스트에서 10~300자와 4어절 이상 조건을 적용합니다. `word_num` 열이 있으면 해당 값을 사용하고, 열이 없는 표 형식 입력에서는 공백 기준으로 어절 수를 계산합니다. 동일 텍스트의 첫 행을 남깁니다.
4. 배포본의 두 집합을 합친 다음 `doc_id` 기준으로 다시 분할합니다. 먼저 5개 폴드 중 첫 폴드를 평가셋으로 사용합니다. 나머지에서 10개 폴드 중 첫 폴드를 검증셋으로 사용하고, 나머지를 학습셋으로 사용합니다. 두 단계 모두 레이블 비율을 고려하는 그룹 분할(`StratifiedGroupKFold`)과 시드 42를 사용합니다. 분할기에 필요한 조건을 충족하지 못하는 입력의 경우 `GroupShuffleSplit`으로 같은 문서가 한 세트에만 들어가도록 분할하고, 사용한 방법을 보고서에 기록합니다.

기존 실험에서 생성한 Parquet 또는 CSV가 있으면 중간 파일에서 시작할 수 있습니다. 표 형식 입력에는 `text`, `category`, `doc_id` 열이 필요합니다.

```sh
python prepare_aihub.py --flattened "data/aihub/sentence_type_experiment_ready_20260507_134733.parquet" --output out/aihub-from-table
```

## NSMC

[NSMC 공식 저장소](https://github.com/e9t/nsmc)의 `ratings_train.txt`와 `ratings_test.txt`를 같은 폴더에 둡니다.

```sh
python prepare_nsmc.py --input data/nsmc --output out/nsmc
```

1. 각 파일에서 레이블이 0(부정) 또는 1(긍정)인 행을 사용합니다. 폭이 0인 공백(U+200B)과 연속 공백을 정리하고, 연속된 동일 한글 자모 또는 동일 문장부호(`!?.~,`)는 두 글자까지만 남깁니다.
2. 6~300자와 4어절 이상인 문장을 사용합니다. 각 파일 안에서 동일한 정제 문장에 두 감성 레이블이 있는 경우 그 문장의 행을 모두 제거합니다. 이후 동일한 정제 문장의 첫 행을 남깁니다.
3. 정제된 학습·평가에 공통으로 나타나는 문장은 학습 쪽에서 제거합니다. 남은 공식 학습 데이터의 10%를 감성 레이블 비율에 맞춰 시드 42로 검증셋에 배정합니다. 평가셋은 공식 평가 파일에서 정제한 행으로 구성합니다. 합본 `ratings.txt`가 있으면 ID 집합의 일치 여부를 확인하는 데 사용합니다.

## 출력과 검증

새 출력 디렉터리에 `train.csv`, `valid.csv`, `test.csv`, `preprocessing_report.json`을 생성합니다. JSON 보고서에 필터링 단계별 건수와 세트별 레이블 분포를 기록합니다. AI-Hub는 문서 그룹과 문장의 세트 간 중복을, NSMC는 정제 문장의 세트 간 중복을 검사합니다.

| 데이터셋 | 학습 | 검증 | 평가 |
| --- | ---: | ---: | ---: |
| AI-Hub | 103,150 | 11,739 | 29,009 |
| NSMC | 98,959 | 10,996 | 36,794 |

`reference_counts.csv`에서 세트별 전체 건수(`ALL`)와 레이블별 건수를 비교할 수 있습니다. 기존 AI-Hub Parquet와 NSMC 학습·평가 파일에서 새로 분할한 결과는 기존 실험 분할 파일의 문장, 레이블, 행 순서와 일치했습니다. AI-Hub의 JSON 변환 경로는 학습용과 검증용 원본 각 1개 문서에서 추출된 39개 행을 기존 Parquet와 대조하고, 합성 JSON으로 분할까지 실행했습니다.

다음은 검증에 사용한 입력 파일의 SHA-256입니다.

```text
0a5ec47011891c1bbe36cce88fda8d2d3f2775dcf0f4592f4d38e5290300e255  sentence_type_experiment_ready_20260507_134733.parquet
e03b7d14e9e41be8d464a28057cd25d7396c53e67aa7fd5f7e552c59b0ee2940  ratings_train.txt
8ac9f64052f11dbf6ae0acb5e038f03d90a76f0eda7820cfb3a92d02edfcebda  ratings_test.txt
```

## 합성 데이터로 실행하기

```sh
python examples/make_sample_inputs.py sample_data
python prepare_aihub.py --training-labels "sample_data/aihub/Training/02.라벨링데이터" --validation-labels "sample_data/aihub/Validation/02.라벨링데이터" --output out/sample-aihub
python prepare_nsmc.py --input sample_data/nsmc --output out/sample-nsmc
```

예제에서 학습·검증·평가 건수는 각각 AI-Hub 206·24·58, NSMC 90·11·24입니다.
