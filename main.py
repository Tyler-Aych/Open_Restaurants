from fastapi import FastAPI
from datetime import datetime

app = FastAPI()


@app.get("/{url_date}")
def find_restaurants(url_date):
    #date_given = '2021-01-18T091508'
    date_converted = datetime.strptime(url_date, "%Y-%m-%dT%H%M%S")
    another_date = datetime.strptime('2021-01-17', "%Y-%m-%d")
    winner = ''
    if date_converted > another_date:
        winner = date_converted
    else:
        winner = another_date
    return {"url_date": url_date}