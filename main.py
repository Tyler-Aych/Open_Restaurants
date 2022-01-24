from fastapi import FastAPI, Depends
from datetime import datetime

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

restr_dict = {
    "The Cowfish Sushi Burger Bar":   "Mon-Sun 11:00 am - 10 pm", #timestart 0
    "Morgan St Food Hall": "Mon-Sun 11 am - 9:30 pm", #timestart 0
    "Beasley's Chicken + Honey":   "Mon-Fri, Sat 11 am - 12 pm / Sun 11 am - 10 pm",
    "Garland": "Tues-Fri, Sun 11:30 am - 2 am / Sat 5:30 pm - 11 pm",
    "Crawford and Son" :   "Mon-Sun 11:30 am - 10 pm", #timstart 0
    "Death and Taxes": "Mon-Sun 5 pm - 10 pm", #timestart 0
    "Caffe Luna":  "Mon-Sun 11 am - 12 am", #timestart 0
    "Bida Manda":  "Mon-Thu, Sun 11:30 am - 10 pm / Fri-Sat 11:30 am - 11 pm",
    "The Cheesecake Factory":  "Mon-Thu 11 am - 11 pm / Fri-Sat 11 am - 12:30 am / Sun 10 am - 11 pm",
    "Tupelo Honey":   "Mon-Thu, Sun 9 am - 10 pm / Fri-Sat 9 am - 11 pm",
    "Player's Retreat":    "Mon-Thu, Sun 11:30 am - 9:30 pm / Fri-Sat 11:30 am - 10 pm",
    "Glenwood Grill":  "Mon-Sat 11 am - 11 pm / Sun 11 am - 10 pm",
    "Neomonde":   "Mon-Thu 11:30 am - 10 pm / Fri-Sun 11:30 am - 11 pm" #timestart 0
}

#handle situations like thurs-tues
#sun to monday

dotw = {
    "Mon": 0,
    "Tues": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6
}

#   "Page Road Grill", Mon-Sun 11 am - 11 pm

# "Mon-Sun 11 am", "11 pm"

# "Mon", "Sun 11 am", "11 pm"


# "Mon-Fri, Sat 11 am - 12 pm / Sun 11 am - 10 pm"

# "Mon-Fri, Sat 11 am - 12 pm" "Sun 11 am - 10 pm"

# "Mon-Fri, Sat 11 am" "12 pm" "Sun 11 am" "10 pm"

# "Mon-Fri" "Sat 11 am" "12 pm" "Sun 11 am" "10 pm"

# "Mon" "Fri" "Sat 11 am" "12 pm" "Sun 11 am" "10 pm"

#   "Mez Mexican", Mon-Fri 10:30 am - 9:30 pm / Sat-Sun 10 am - 9:30 pm
#   "Saltbox", Mon-Sun 11:30 am - 10:30 pm
#   "El Rodeo",   Mon-Sun 11 am - 10:30 pm
#   "Provence" ,   Mon-Thu, Sun 11:30 am - 9 pm / Fri-Sat 11:30 am - 10 pm
#   "Bonchon", Mon-Wed 5 pm - 12:30 am / Thu-Fri 5 pm - 1:30 am / Sat 3 pm - 1:30 am / Sun 3 pm - 11:30 pm
#   "Tazza Kitchen", Mon-Sun 11 am - 10 pm
#   "Mandolin",    Mon-Thu 11 am - 10 pm / Fri-Sat 10 am - 10:30 pm / Sun 11 am - 11 pm
#   "Mami Nora's", Mon-Sat 11 am - 10 pm / Sun 12 pm - 10 pm
#   "Gravy",   Mon-Sun 11 am - 10 pm
#   "Taverna Agora",   Mon-Thu, Sun 11 am - 10 pm / Fri-Sat 11 am - 12 am
#   "Char Grill",  Mon-Fri 11:30 am - 10 pm / Sat-Sun 7 am - 3 pm
#   "Seoul 116",  Mon-Sun 11 am - 4 am
#   "Whiskey Kitchen", Mon-Thu, Sun 11:30 am - 10 pm / Fri-Sat 11:30 am - 11 pm
#   "Sitti",  Mon-Sun 11:30 am - 9:30 pm
#   "Stanbury",    Mon-Sun 11 am - 12 am
#   "Yard House",  Mon-Sun 11:30 am - 10 pm
#   "David's Dumpling",    Mon-Sat 11:30 am - 10 pm / Sun 5:30 pm - 10 pm
#   "Gringo a Gogo",   Mon-Sun 11 am - 11 pm
#   "Centro",  Mon, Wed-Sun 11 am - 10 pm
#   "Brewery Bhavana", Mon-Sun 11 am - 10:30 pm
#   "Dashi",   Mon-Fri 10 am - 9:30 pm / Sat-Sun 9:30 am - 9:30 pm
#   "42nd Street Oyster Bar",  Mon-Sat 11 am - 12 am / Sun 12 pm - 2 am
#   "Top of the Hill", Mon-Fri 11 am - 9 pm / Sat 5 pm - 9 pm
#   "Jose and Sons",   Mon-Fri 11:30 am - 10 pm / Sat 5:30 pm - 10 pm
#   "Oakleaf", Mon-Thu, Sun 11 am - 10 pm / Fri-Sat 11 am - 11 pm
#   "Second Empire",   Mon-Fri 11 am - 10 pm / Sat-Sun 5 pm - 10 pm

#first split(" / ")
  #this will give each day and time pair
#next split(" - ")
  # this will split the - between times only
#next split(", ")
  # this will split up multiple weekday groupings
#then split("-")
  # this separates week ranges

# "Mon", "Sun 11 am", "11 pm"

#for this issue you can use the second if statement to capture the diff
#"Mon, Wed-Sun 11 am - 10 pm"
#"Mon-Fri, Sat 11 am - 12 pm / Sun 11 am - 10 pm",

#"Mon-Fri, Sat 11 am - 12 pm" "Sun 11 am - 10 pm"

#"Mon-Fri, Sat 11 am" 
#"12 pm" 
#"Sun 11 am" 
#"10 pm"

# "Mon" "Fri" "Sat 11 am" "12 pm" "Sun 11 am" "10 pm"

#"Mon, Wed-Sun 11 am - 10 pm"
#"Mon-Fri, Sat 11 am - 12 pm / Sun 11 am - 10 pm",

def is_open(given_day, given_time, restr_datetime):
    
    split_by_dayandtime = restr_datetime.split(" / ")
    date_found = False
    time_start = 0
    next_day_num = 0

    for split_dt in split_by_dayandtime:
        
        date_found = False
        split_by_times = split_dt.split(" - ")
        split_by_weekday_groups = split_by_times[0].split(", ")

        if len(split_by_times[1].split(":")) > 1:
            time_end = datetime.strptime(split_by_times[1], "%I:%M %p")
            print('time end: ', time_end)
        else:
            time_end = datetime.strptime(split_by_times[1], "%I %p")
            print('time end: ', time_end)
        
        #if there is a day, day
        for count, weekday_grp in enumerate(split_by_weekday_groups):
            print('Group ', count, ' : ', weekday_grp)
            split_by_week_ranges = weekday_grp.split("-")
            

            # pattern: day-day
            if len(split_by_week_ranges) > 1:
                
                day_separated = split_by_week_ranges[1].split(" ", 1)

                if given_day >= dotw[split_by_week_ranges[0]] and given_day <= dotw[day_separated[0]]:
                    print('it is between: ', split_by_week_ranges[0], 'and ', day_separated[0])
                    print('it is between: ', dotw[split_by_week_ranges[0]], 'and ', dotw[day_separated[0]])
                    print('split_by_week_ranges[1]: ', split_by_week_ranges[1])
                    print('before separation of space: ', split_by_week_ranges[1])
                    print('day separated[0]: ', day_separated[0])
                    print('dotw[split_by_week_ranges[0]]: ', dotw[split_by_week_ranges[0]])
                    date_found = True

                # check the time and make sure to check if it goes into the next day
                if len(day_separated) > 1:
                    if len(day_separated[1].split(":")) > 1:
                        time_start = datetime.strptime(day_separated[1], "%I:%M %p")
                        print('time start0: ', time_start)
                    else:
                        time_start = datetime.strptime(day_separated[1], "%I %p")
                        print('time start1: ', time_start)
                    if time_start > time_end:
                        # check if the url_datetime is actually the next day
                        print(time_start, ' was greater than ', time_end)
                        if dotw[day_separated[0]] == 6:
                            next_day_num = 0
                        else:
                            next_day_num = dotw[day_separated[0]] + 1
                        print('next_day_num: ', next_day_num)
                        if given_day == next_day_num:
                            temp_time_start = time_start.replace(hour=0, minute=0)
                            print('The new temp start time: ', temp_time_start, ' The end time: ', time_end, ' and given time is: ', given_time)
                            if given_time >= temp_time_start and given_time <= time_end:
                                return True
                        else:
                            time_end = time_end.replace(hour=23, minute=59)
                            print('new time end: ', time_end)
                    if date_found and given_time >= time_start and given_time <= time_end:
                        return True

            # pattern: day, day-day?
            else:
                day_separated = split_by_week_ranges[0].split(" ", 1)
                if given_day == dotw[day_separated[0]]:
                    date_found = True
                if len(day_separated) > 1:
                    print('else statement reached, the day is', day_separated[0], ' or ', dotw[day_separated[0]])
                    print('day + 1', dotw[day_separated[0]] + 1)
                    print('and the current given day is: ', given_day)
                    day_separated = split_by_week_ranges[0].split(" ", 1)

                    if dotw[day_separated[0]] == 6:
                        next_day_num = 0
                    else:
                        next_day_num = dotw[day_separated[0]] + 1

                    print('next_day_num: ', next_day_num)
                    if date_found or given_day == next_day_num:
                        print("it is equal to: ", day_separated[0], ' or ', dotw[day_separated[0]], 'in number format')
                        if len(day_separated[1].split(":")) > 1:
                            time_start = datetime.strptime(day_separated[1], "%I:%M %p")
                            print('timestart: ', time_start)
                        else:
                            time_start = datetime.strptime(day_separated[1], "%I %p")
                            print('timestart: ', time_start)
                        if time_start > time_end:
                            print(time_start, ' was greater2 than ', time_end)
                            print('next_day_num: ', next_day_num)

                            if given_day == next_day_num:
                                temp_time_start = time_start.replace(hour=0, minute=0)
                                print('The new temp start time: ', temp_time_start, ' The end time: ', time_end, ' and given time is: ', given_time)
                                if given_time >= temp_time_start and given_time <= time_end:
                                    return True
                            else:
                                time_end = time_end.replace(hour=23, minute=59)
                                print('new time end: ', time_end)
                        if given_time >= time_start and given_time <= time_end:
                            return True
                  
    return False



@app.get("/{url_date}")
def find_restaurants(url_date, db: Session = Depends(get_db)):
    #db = get_db()
    db_restaurant_list = db.query(models.Restaurant).all()
    #def read_user(user_id: int, db: Session = Depends(get_db)):
    #db.query(models.Restaurant).all()
    #db_user = crud.get_user(db, user_id=user_id)
    #models.
    #db_restaurants = models.Restaurant.db.query().all()
    if db_restaurant_list is None:
        raise HTTPException(status_code=404, detail="No restaurants found.")

    #date_given = '2021-01-18T091508'
    #restr_tuples = rest_dict.items()
    
    #This will take the inputted date from the api endpoint and convert it to a datetime
    date_converted = datetime.strptime(url_date, "%Y-%m-%dT%H%M%S")
    restaurants_open = []

    #This will convert the date from the url into a day of the week represented by an integer 0-6, Mon-Sun
    url_day = datetime.weekday(date_converted)
    url_time_dtobj = date_converted.strftime('%H%M')
    url_time = datetime.strptime(url_time_dtobj, '%H%M')

    for restaurant_db in db_restaurant_list:
        print('\n\n\n')
        print(restaurant_db.restaurant)
        print(restaurant_db.hours)
        if is_open(url_day, url_time, restaurant_db.hours):
            restaurants_open.append(restaurant_db.restaurant)
    # for key, value in restr_dict.items():
    #     print('\n\n\n\n')
    #     print(key)
    #     if is_open(url_day, url_time, value):
    #         restaurants_open.append(key)
    #print('database: ', db_restaurants.restaurant)
    print('time given: ', url_time)
    print('given day:', date_converted.strftime('%A'))
    print('given day:', url_day)
    return restaurants_open