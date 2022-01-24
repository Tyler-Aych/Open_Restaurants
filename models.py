from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Restaurant(Base):
    __tablename__ = "Restaurants"

    id = Column(Integer, primary_key=True, index=True)
    restaurant = Column(String, unique=True, index=True)
    hours = Column(String, nullable=False)

    def __init__(self, restaurant, hours):
        self.restaurant = restaurant
        self.hours = hours

# Other databases can be added here
