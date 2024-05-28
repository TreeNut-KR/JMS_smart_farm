from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import calendar
import math
import uvicorn
from datetime import datetime, timedelta
from typing import Optional

# 날짜 데이터 모델
class DateItem(BaseModel):
    created_at: Optional[str] = None

app = FastAPI()

def get_week_dates(year: int, month: int, select: int):
    # 기존 코드에서 날짜 리스트를 계산하는 로직
    first_day_of_month, days_in_month = calendar.monthrange(year, month)
    if first_day_of_month != 0:
        first_day_of_month_week = 8 - first_day_of_month
    else:
        first_day_of_month_week = first_day_of_month + 1

    week_date = first_day_of_month_week + ((select - 1) * 7)
    if 0 >= week_date or days_in_month < week_date:
        return None

    week_select = f"{year}-{month:02d}-{week_date:02d}"
    start_of_week = datetime.strptime(week_select, "%Y-%m-%d")
    end_of_week = start_of_week + timedelta(days=6)

    week_dates = [start_of_week + timedelta(days=i) for i in range((end_of_week - start_of_week).days + 1)]
    return week_dates

@app.get("/week-dates/{year}/{month}/{week}", response_model=List[DateItem])
def week_dates(year: int, month: int, week: int):
    dates = get_week_dates(year, month, week)
    if dates is None:
        return [{"created_at": None} for _ in range(7)]
    return [{"created_at": date.strftime("%Y-%m-%d")} for date in dates]

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8008)