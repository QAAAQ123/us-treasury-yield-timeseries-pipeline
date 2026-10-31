"""
정제된 데이테 프레임을 활용해서 지정된 디렉토리로 CSV 적재 및 CSV 증분 적재 수행
"""
import pandas as pd

"""
### 1. 최초 적재
1. 아카이브 및 연월별 일드 커브 DataFrame 수집(완료 가정)
2. 수집한 DataFrame을 하나의 DataFrame으로 병합(완료 가정)
3. 날짜 기준 오름차순 정렬
4. 일드 스프레드 계산 및 별도 DataFrame 생성
5. 일드 커브 및 일드 스프레드 CSV 각각 저장
### 2. 증분 적재
1. 신규 연월 일드 커브 DataFrame 수집(완료 가정)
3. 일드 스프레드 계산 및 별도 DataFrame 생성
4. 기존 CSV를 DataFrame으로 변환
5. 기존 데이터에서 신규 수집 대상 연월과 이전 전체 데이터 분리
6. 기존 연월 데이터와 신규 수집 데이터 비교
7. 중복 날짜가 존재하는 경우 신규 수집 데이터 기준으로 갱신
8. 이전 전체 데이터와 갱신된 연월 데이터를 병합
9. 날짜 기준 오름차순 정렬
10. 일드 커브 및 일드 스프레드 CSV 각각 갱신
"""

#가정: 전체 수집이 완료된 DataFrame이 입력으로 들어온다고 가정
def initialize_csv(df: pd.DataFrame) -> None:
    """통합된 DataFrame을 기반으로 초기 CSV를 적재한다. 

    전체 기간의 Yield Curve DataFrame을 받아
    Yield Curve 와 Yield Spread CSV를 생성한다.
    """
    pass


#가정: 전체 수집이 완료된 DataFrame이 입력으로 들어온다고 가정
def update_csv(df: pd.DataFrame) -> None:
    """신규 DataFrame을 기존 CSV에 반영한다.
    
    연월별 Yield Curve DataFrame과 기존 CSV를 기반으로
    신규 데이터를 Yield Curve 및 Yield Spread CSV에 증분한다.
    """
    pass
