# Supplementary Materials

한국어 사전학습 언어모델 백도어 공격 실험의 전처리 코드 및 결과 데이터입니다.

## 파일 구성

### `preprocessing/`
데이터셋(AI-Hub, NSMC) 정제 및 분할 스크립트. 원본 데이터는 별도 다운로드 필요.
- `prepare_aihub.py` : AI-Hub 문장 유형 판단 데이터 전처리 및 분할
- `prepare_nsmc.py` : NSMC 전처리 및 분할
- `preprocessing_common.py` : 공통 저장/검증 함수
- `reference_counts.csv` : 데이터셋·분할·레이블별 문장 수
- `requirements.txt` : 전처리 실행 패키지 목록

원본 데이터 출처:
- AI-Hub: https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71486
- NSMC: https://github.com/e9t/nsmc

### `results/`
실험 조건 및 오염률별 측정 결과.
- `experiment_conditions.csv` : 조건(A–D)·시드별 모델, 데이터셋, 학습 설정
- `clean_baselines.csv` : 오염률 0% 기준 평가 결과 (91행)
- `all_poison_rates.csv` : 오염률별 전체 시험점 평가 결과 (784행)

### `results/text_metrics/`
트리거 적용 전후 문장 변환 지표 집계.
- `surface_and_semantic_summary.csv` : 문자 편집 거리, 어절 수 차이, 의미 유사도 중앙값
- `matched_inputs_summary.csv` : NSMC 동일 입력(1,652건) 기준 변환 지표 및 첫 도달 오염률
- `language_model_score_summary.csv` : 종결형 트리거(E1–E3) 토큰당 의사 음의 로그우도 차이 및 95% 신뢰구간

### `supplement/`
보충표 CSV 파일.
- `S1_threshold_sensitivity.csv` : ΔASR 기준값(0.70, 0.75, 0.80)별 첫 도달 오염률
- `S2_evaluation_metrics.csv` : 조건·시드·트리거별 첫 도달점(또는 최대 시험점) 평가 지표
- `S3_natural_occurrence.csv` : 학습셋 전체 및 레이블별 트리거 자연발생률(NOR)과 출현 건수
- `S4_aihub_class_f1.csv` : AI-Hub 정상 평가셋 6개 범주별 F1
- `S5_token_retention.csv` : 128토큰 제한에서의 트리거 보존율
