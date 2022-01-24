import csv
import datetime

import models
from database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

with open("RestarauntHours.csv", "r") as f:
    csv_reader = csv.DictReader(f)

    for row in csv_reader:
        db_record = models.Restaurant(
            restaurant=row["Restaurants"],
            hours=row["Hours"],
        )
        db.add(db_record)

    db.commit()

db.close()