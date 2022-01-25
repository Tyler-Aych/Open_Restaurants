# external modules
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

# internal modules
from database import SessionLocal, engine
import models

# Creates all db tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# converts abbr days into integers
dotw = {
    "Mon": 0,
    "Tues": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6
}

# Converts datetime string api endpoint into a day of the week represented by an integer 0-6, Mon-Sun
def convert_to_day(date_string):
    date_converted = datetime.strptime(date_string, "%Y-%m-%dT%H%M%S")
    
    return datetime.weekday(date_converted)

# Converts datetime string api endpoint into a time
def convert_to_time(date_string):
    date_converted = datetime.strptime(date_string, "%Y-%m-%dT%H%M%S")
    url_time_dtobj = date_converted.strftime('%H%M')
    
    return datetime.strptime(url_time_dtobj, '%H%M')

# Checks if any restaurants are open during the given datetime
def is_open(given_day, given_time, restr_datetime):
    
    split_by_dayandtime = restr_datetime.split(" / ")
    time_start = 0
    next_day_num = 0

    for split_dt in split_by_dayandtime:
        
        date_found = False
        split_by_times = split_dt.split(" - ")
        split_by_weekday_groups = split_by_times[0].split(", ")

        if len(split_by_times[1].split(":")) > 1:
            time_end = datetime.strptime(split_by_times[1], "%I:%M %p")
        else:
            time_end = datetime.strptime(split_by_times[1], "%I %p")
        
        #if there is a day, day
        for count, weekday_grp in enumerate(split_by_weekday_groups):
            split_by_week_ranges = weekday_grp.split("-")
            

            # pattern: day-day
            if len(split_by_week_ranges) > 1:
                
                day_separated = split_by_week_ranges[1].split(" ", 1)

                if given_day >= dotw[split_by_week_ranges[0]] and given_day <= dotw[day_separated[0]]:
                    date_found = True

                # check the time and make sure to check if it goes into the next day
                if len(day_separated) > 1:
                    if len(day_separated[1].split(":")) > 1:
                        time_start = datetime.strptime(day_separated[1], "%I:%M %p")
                    else:
                        time_start = datetime.strptime(day_separated[1], "%I %p")
                    if time_start > time_end:
                        # check if the url_datetime is actually the next day
                        if dotw[day_separated[0]] == 6:
                            next_day_num = 0
                        else:
                            next_day_num = dotw[day_separated[0]] + 1
                        if given_day == next_day_num:
                            temp_time_start = time_start.replace(hour=0, minute=0)
                            if given_time >= temp_time_start and given_time <= time_end:
                                return True
                        else:
                            time_end = time_end.replace(hour=23, minute=59)
                    if date_found and given_time >= time_start and given_time <= time_end:
                        return True

            # pattern: day, day-day?
            else:
                day_separated = split_by_week_ranges[0].split(" ", 1)
                if given_day == dotw[day_separated[0]]:
                    date_found = True
                if len(day_separated) > 1:
                    day_separated = split_by_week_ranges[0].split(" ", 1)

                    if dotw[day_separated[0]] == 6:
                        next_day_num = 0
                    else:
                        next_day_num = dotw[day_separated[0]] + 1

                    if date_found or given_day == next_day_num:
                        if len(day_separated[1].split(":")) > 1:
                            time_start = datetime.strptime(day_separated[1], "%I:%M %p")
                        else:
                            time_start = datetime.strptime(day_separated[1], "%I %p")
                        if time_start > time_end:
                            if given_day == next_day_num:
                                temp_time_start = time_start.replace(hour=0, minute=0)
                                if given_time >= temp_time_start and given_time <= time_end:
                                    return True
                            else:
                                time_end = time_end.replace(hour=23, minute=59)
                        if given_time >= time_start and given_time <= time_end:
                            return True
                  
    return False


# The main function since our api has one function
@app.get("/{url_date}")
def find_restaurants(url_date, db: Session = Depends(get_db)):
    
    restaurants_open = []
    
    try:
        url_day = convert_to_day(url_date)
        url_time = convert_to_time(url_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Your date does not follow the format: YYYY-MM-DDTHHMMSS")

    db_restaurant_list = db.query(models.Restaurant).all()
    if db_restaurant_list is None:
        raise HTTPException(status_code=404, detail="No restaurants found.")

    for restaurant_db in db_restaurant_list:
        if is_open(url_day, url_time, restaurant_db.hours):
            restaurants_open.append(restaurant_db.restaurant)
    return restaurants_open



#########################################################################################################
##                                                                                                     ##
##                                                                                                     ##
##                                           Unit Test Section                                         ##                                           
##                                                                                                     ##
##                                                                                                     ##
#########################################################################################################

#command: python -m pytest main.py

client = TestClient(app)


def test_wrong_date_format():
    response = client.get("/2022-01-24")
    assert response.status_code == 400

def test_correct_date_format():
    response = client.get("/2022-01-20T101523")
    assert response.status_code == 200

def test_correct_date_without_seconds():
    response = client.get("/2022-01-20T1015")
    assert response.status_code == 200

def test_after_midnight():
    response = client.get("/2022-01-24T013511")
    assert response.status_code == 200
    assert response.json() == ["Seoul 116","42nd Street Oyster Bar"]

def test_one_day_one_time():
    rest_hours = 'Mon 11 am - 12 pm'

    #lower bound (Mon 11:01 am)
    user_date = '2022-01-24T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Mon 10:59 am)
    user_date = '2022-01-24T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Mon 11:59 am)
    user_date = '2022-01-24T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Mon 12:01 pm)
    user_date = '2022-01-24T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

def test_one_day_range_one_time():
    rest_hours = 'Mon-Wed 11 am - 12 pm'

    ## Monday
    #lower bound (Mon 11:01 am)
    user_date = '2022-01-24T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Mon 10:59 am)
    user_date = '2022-01-24T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Mon 11:59 am)
    user_date = '2022-01-24T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Mon 12:01 pm)
    user_date = '2022-01-24T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False


    ## Tuesday
    #lower bound (Tues 11:01 am)
    user_date = '2022-01-25T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Tues 10:59 am)
    user_date = '2022-01-25T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #middle day upper bound (Tues 11:59 am)
    user_date = '2022-01-25T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #middle day beyond upper bound (Tues 12:01 pm)
    user_date = '2022-01-25T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False


    ## Wednesday
    #lower bound (Wed 11:01 am)
    user_date = '2022-01-26T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Wed 10:59 am)
    user_date = '2022-01-26T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Wed 11:59 am)
    user_date = '2022-01-26T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Wed 12:01 pm)
    user_date = '2022-01-26T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

def test_two_days_one_time():
    rest_hours = 'Mon, Wed 11 am - 12 pm'

    ## Monday
    #lower bound (Mon 11:01 am)
    user_date = '2022-01-24T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Mon 10:59 am)
    user_date = '2022-01-24T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Mon 11:59 am)
    user_date = '2022-01-24T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Mon 12:01 pm)
    user_date = '2022-01-24T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False


    ## Tuesday
    #within time bound (Tues 11:01 am)
    user_date = '2022-01-25T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False


    ## Wednesday
    #lower bound (Wed 11:01 am)
    user_date = '2022-01-26T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Wed 10:59 am)
    user_date = '2022-01-26T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Wed 11:59 am)
    user_date = '2022-01-26T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Wed 12:01 pm)
    user_date = '2022-01-26T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

def test_two_days_two_times():
    rest_hours = 'Mon 11 am - 10 pm / Sun 12 pm - 10 pm'

    ## Monday
    #lower bound (Mon 11:01 am)
    user_date = '2022-01-24T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Mon 10:59 am)
    user_date = '2022-01-24T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Mon 9:59 pm)
    user_date = '2022-01-24T215900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Mon 10:01 pm)
    user_date = '2022-01-24T220100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False


    ## Sunday
    #lower bound (Sun 12:01 pm)
    user_date = '2022-01-23T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Sun 11:59 am)
    user_date = '2022-01-23T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Sun 9:59 pm)
    user_date = '2022-01-23T215900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Sun 10:01 pm)
    user_date = '2022-01-23T220100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

def test_midnight_start():
    rest_hours = 'Mon 12 am - 4 am'

    #lower bound (Mon 12:01 am)
    user_date = '2022-01-24T000100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Sun 11:59 pm)
    user_date = '2022-01-23T235900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Mon 3:59 am)
    user_date = '2022-01-24T035900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Mon 4:01 am)
    user_date = '2022-01-24T040100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

def test_all_days_past_midnight():
    rest_hours = 'Mon 11 am - 2 am / Sun 12 pm - 10:58 am'

    ## Monday/Tuesday
    #lower bound (Mon 11:01 am)
    user_date = '2022-01-24T110100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Mon 10:59 am)
    user_date = '2022-01-24T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Tues 1:59 am)
    user_date = '2022-01-25T015900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Tues 2:01 am)
    user_date = '2022-01-25T020100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False


    ## Sunday/Monday
    #lower bound (Sun 12:01 pm)
    user_date = '2022-01-23T120100'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond lower bound (Sun 11:59 am)
    user_date = '2022-01-23T115900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False

    #upper bound (Mon 10:57 am)
    user_date = '2022-01-24T105700'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == True

    #beyond upper bound (Mon 10:59:01 am)
    user_date = '2022-01-24T105900'
    day = convert_to_day(user_date)
    time = convert_to_time(user_date)
    assert is_open(day, time, rest_hours) == False