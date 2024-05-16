import calendar
import math
def get_week(year, month, select=0):
    '''
    first_day_of_month => (0: 월요일, 1: 화요일, ..., 6: 일요일)

    '''
    print(f"{month}월 {select}주차 선택\n")
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
    week_select = first_day_of_mont_week+((select-1)*7)
    if 0 >= week_select or days_in_month < week_select:
        return week, week_dict, None
    return week, week_dict, week_select

if __name__ == "__main__":
    year = 2024
    month = 10
    month_week, week_dict, week_select = get_week(year, month, -1)
    print(f"{year}년 {month}월의 주차: {month_week}주차")
    for key, value in week_dict.items():
        print(f"{key}주차 월요일 {value}일")


    print(week_select)
    


[
  {
    "Week_temperature": 25.5,
    "Week_humidity": 60.2,
    "Week_ground1": 15.3,
    "Week_ground2": 18.7,
    "All_ceated_at": "2023-05-01"
  },
  {
    "Week_temperature": 24.8,
    "Week_humidity": 58.1,
    "Week_ground1": 16.1,
    "Week_ground2": 17.9,
    "All_ceated_at": "2023-05-02"
  },
  {
    "Week_temperature": null,
    "Week_humidity": null,
    "Week_ground1": null,
    "Week_ground2": null,
    "All_ceated_at": "2023-05-03"
  },
  {
    "Week_temperature": null,
    "Week_humidity": null,
    "Week_ground1": null,
    "Week_ground2": null,
    "All_ceated_at": "2023-05-04"
  },
  {
    "Week_temperature": null,
    "Week_humidity": null,
    "Week_ground1": null,
    "Week_ground2": null,
    "All_ceated_at": "2023-05-05"
  },
  {
    "Week_temperature": 26.2,
    "Week_humidity": 62.3,
    "Week_ground1": 14.8,
    "Week_ground2": 19.2,
    "All_ceated_at": "2023-05-06"
  },
  {
    "Week_temperature": 25.9,
    "Week_humidity": 61.7,
    "Week_ground1": 15.1,
    "Week_ground2": 18.9,
    "All_ceated_at": "2023-05-07"
  }
]
