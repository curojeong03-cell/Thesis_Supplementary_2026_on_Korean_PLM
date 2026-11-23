# 제5장 문장 변환 지표

| 파일 | 학위논문 표 | 범위와 단위 |
|---|---|---|
| [surface_and_semantic_summary.csv](surface_and_semantic_summary.csv) | 표 5-1, 표 5-2 | AIHUB·NSMC의 일곱 트리거별 문자 편집 거리(글자), 정규화 문자 편집 거리, 어절 수 차이 및 임베딩 코사인 유사도의 중앙값. 해당 표의 자릿수를 유지하였다. |
| [matched_inputs_summary.csv](matched_inputs_summary.csv) | 표 5-3 | NSMC 긍정 목표·시드 42의 동일 부정 리뷰 1,652개에 대한 중앙값과 첫 도달점의 관측 오염률(%) 및 ΔASR. 문자 수 차이는 변환문에서 원문을 뺀 값이다. |
| [language_model_score_summary.csv](language_model_score_summary.csv) | 표 5-4 | 동일한 부정 리뷰에서 채점 표본 507개 중 세 종결 표현의 점수가 모두 유효한 448개. 토큰당 평균 의사 음의 로그우도 차이(변환문 − 원문)의 중앙값과 10,000회 복원추출로 구한 95% 백분위 신뢰구간. |

CSV는 논문 표의 집계를 담고 있다.
