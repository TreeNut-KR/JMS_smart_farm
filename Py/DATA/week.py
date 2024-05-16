import calendar
import math
def get_week(year, month):
    '''
    first_day_of_month => (0: 월요일, 1: 화요일, ..., 6: 일요일)

    '''
    print(f"{month}월 선택\n")
    week_num = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
    }
    first_day_of_month, days_in_month = calendar.monthrange(year, month)
    print(f"첫 날 요일  : {week_num.get(first_day_of_month)}")
    print(f"마지막 날   : {days_in_month}일")

    if first_day_of_month != 0:
        first_day_of_mont_week = 8-first_day_of_month
    else:
        first_day_of_mont_week = first_day_of_month+1

    week= math.ceil(((days_in_month)-first_day_of_mont_week)/7)
    week_dict = {i+1: first_day_of_mont_week+(i*7) for i in range(0, week)}
    return week, week_dict

year = 2024
month = 10
first_week, week_dict = get_week(year, month)
print(f"{year}년 {month}월의 주차: {first_week}주차")
for key, value in week_dict.items():
    print(f"{key}주차 월요일 {value}일")