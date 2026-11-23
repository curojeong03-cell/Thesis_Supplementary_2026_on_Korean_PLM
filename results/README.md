# 실험 조건과 오염률별 결과

제4장의 비교 조건 A·B·C·D와 학위논문 부록 2~6에 해당하는 측정값이다. 한 행은 조건, 학습 시드, 트리거, 명목 오염률의 한 조합이다. 각 조합에서 실제 시험한 오염률만 기록하였다. 시드나 트리거에 따라 시험한 오염률의 간격과 개수가 다르다.

| 파일 | 담긴 내용 |
|---|---|
| [all_poison_rates.csv](all_poison_rates.csv) | 0%를 초과하는 전체 시험점 784개의 ASR, ΔASR, 정상 문장 Macro-F1과 정확도 |
| [clean_baselines.csv](clean_baselines.csv) | 오염률 0%에서 조건·시드·트리거별 참조값 91행 |
| [experiment_conditions.csv](experiment_conditions.csv) | 조건·시드별 말뭉치, 분류 모델, 오염 문장 후보군, 목표 레이블, 평가 규모 및 학습 설정 |
| [chapter5](chapter5/) | 학위논문 제5장의 문자·어절 편집, 의미 유사도 및 언어모델 점수 집계 |

## 조건과 부록의 대응

| 학위논문 부록 | CSV의 condition | 말뭉치 | 분류 모델 | 후보군 | 학습 시드 | 시험점 |
|---|---|---|---|---|---|---:|
| 부록 2 | A | AIHUB | KLUE-RoBERTa | 공통 | 42·52·62 | 173 |
| 부록 3 | B | AIHUB | KoELECTRA | 공통 | 42·52·62 | 199 |
| 부록 4 | C | AIHUB | KLUE-RoBERTa | 트리거별 | 42 | 80 |
| 부록 5 | D positive | NSMC | KLUE-RoBERTa | 공통 | 42·52·62 | 173 |
| 부록 6 | D negative | NSMC | KLUE-RoBERTa | 공통 | 42·52·62 | 159 |

A·B·C의 목표 레이블은 IT·과학(`target_it_science`)이다. D는 긍정 목표(`positive`)와 부정 목표(`negative`)로 구분한다. 후보군 이름 `universal_core`는 공통 후보군, `natural_coverage`는 트리거별 후보군을 뜻한다. 조건과 학습 시드를 키로 결과 파일과 실험 조건 파일의 행을 연결할 수 있다.

## 지표와 단위

| 열 | 정의 |
|---|---|
| `nominal_poison_rate_pct` | 실험에서 설정한 오염률(%). 예를 들어 0.075는 0.075%를 뜻한다. |
| `actual_poison_rate_pct`, `poisoned_train_n` | 학습 문장 중 실제로 오염된 비율(%)과 문장 수. 실제 오염률은 100 × 오염 문장 수 ÷ 전체 학습 문장 수이다. |
| `attack_model_asr`, `clean_model_asr` | 같은 변환 평가 입력에서 오염 모델과 정상 모델이 각각 목표 레이블을 예측한 비율(0~1). |
| `delta_asr` | 오염 모델의 ASR에서 정상 모델의 ASR을 뺀 값. 예를 들어 0.80은 80%포인트 차이다. |
| `clean_macro_f1`, `clean_accuracy` | **오염 모델**을 변환하지 않은 평가 입력에서 평가한 Macro-F1 및 정확도(0~1). |
| `clean_model_macro_f1`, `clean_model_accuracy` | **정상 모델**을 같은 원래 평가 입력에서 평가한 기준값(0~1). AIHUB는 저장된 기준 기록을 사용했고, NSMC는 통합 결과의 점수에 기록된 감소량을 더해 기준값을 구했다. |
| `attack_eval_n`, `clean_eval_n` | ASR 평가용 변환 문장 수와 정상 문장 성능 평가용 원래 문장 수. |

0% 파일에는 같은 조건과 시드의 정상 문장 성능이 트리거별로 반복된다. 0%에서의 `attack_model_asr` 자리는 비교를 위해 같은 `clean_model_asr`으로 채웠으며, ΔASR은 0이다. 이 91행은 784개 오염 시험점 집계에서 제외한다. 두 결과 파일에는 동일한 열을 썼다.

부록 2~6은 `all_poison_rates.csv`에서 조건·트리거·시드별 명목 오염률을 가로축, `delta_asr`을 세로축으로 그렸다. 가로축은 양의 오염률을 로그 척도로 표시한다. 첫 도달점은 ΔASR이 0.80 이상인 최초의 관측 오염률이다. 0.70·0.75·0.80 기준의 도달점은 [S1](../supplement/S1_threshold_sensitivity.csv), 0.80 기준의 첫 도달점 또는 최대 시험점 상세는 [S2](../supplement/S2_evaluation_metrics.csv)에서 찾아볼 수 있다.

## 검산

저장소 루트에서 `python results/verify_results.py`를 실행하면 CSV의 측정점, 0% 기준값, ΔASR 계산, S1과 S2 집계를 대조한다. Python 표준 라이브러리를 사용한다.
