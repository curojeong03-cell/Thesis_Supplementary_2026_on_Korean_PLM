# 한국어 사전학습 언어모델의 트리거 자연발생률 연구 보충자료

**Relationship Between Trigger Natural Occurrence Rate and Poisoning Efficiency in Backdoor Attacks on Korean Pre-trained Language Models**

한국컴퓨터정보학회 논문 재심 원고의 온라인 보충자료입니다. 트리거 자연발생률(Natural Occurrence Rate, NOR)은 위치와 형태 조건에 맞는 표현이 오염 전 학습셋에 나타난 문장 비율입니다. 이 저장소에는 두 말뭉치의 전처리 코드, 지표와 집계 기준, 보충표 S1–S5를 제공합니다.

## 보충표

| 표 | 내용 | 다운로드 |
|---|---|---|
| S1 | ΔASR 기준값 0.70·0.75·0.80에 따른 첫 도달 오염률 | [표](supplement/S1_threshold_sensitivity.md) · [CSV](supplement/S1_threshold_sensitivity.csv) |
| S2 | 조건·시드·트리거별 첫 도달점 또는 최대 시험점의 평가 결과 | [표](supplement/S2_evaluation_metrics.md) · [CSV](supplement/S2_evaluation_metrics.csv) |
| S3 | 학습셋 전체 및 원래 레이블별 NOR과 출현 건수 | [표](supplement/S3_natural_occurrence.md) · [CSV](supplement/S3_natural_occurrence.csv) |
| S4 | AI-Hub 정상 평가셋의 여섯 범주별 F1 | [표](supplement/S4_aihub_class_f1.md) · [CSV](supplement/S4_aihub_class_f1.csv) |
| S5 | 128토큰 입력 길이 제한에서의 평가 입력 보존율 | [표](supplement/S5_token_retention.md) · [CSV](supplement/S5_token_retention.csv) |

[집계 기준 및 CSV 열 설명](METHODS.md)에서 실험 조건 A–D, 분모, 단위와 미도달 표기 방식을 확인할 수 있습니다. S1의 CSV는 기준값마다 한 행을 사용합니다. S3과 S5의 CSV에는 표에 표시한 반올림 이전의 비율과 세부 건수를 실었습니다.

## 전체 시험점과 학위논문 부록

[실험 결과 안내](results/README.md)에서 조건·시드·트리거별 전체 시험점 784개의 [오염률별 결과 CSV](results/all_poison_rates.csv), [오염률 0% 기준값](results/clean_baselines.csv), [실험 조건](results/experiment_conditions.csv)을 제공합니다. 학위논문 부록 2~6의 곡선은 이 오염률별 결과를 사용했습니다. 학위논문 제5장의 문자 편집, 의미 유사도 및 언어모델 점수는 [문장 변환 지표](results/chapter5/)에서 확인할 수 있습니다.

## 데이터 전처리

[전처리 코드 및 실행 방법](preprocessing/README.md)에 AI-Hub와 NSMC의 분할·정제 절차, 합성 입력 생성 방법, [분할별 기준 건수](preprocessing/reference_counts.csv)를 제공합니다. 원본 말뭉치는 각 배포처에서 내려받습니다. [AI-Hub 데이터](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71486) · [NSMC 공식 저장소](https://github.com/e9t/nsmc)

## 집계 검산

저장소 루트에서 다음 명령을 실행하면 S1–S2의 주 기준 결과, S3의 NOR과 레이블별 분모, S4의 범주별 F1과 Macro-F1, S5의 보존율을 대조합니다. Python 표준 라이브러리를 사용합니다.

```sh
python verify_supplement.py
```
