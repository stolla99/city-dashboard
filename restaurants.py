import re

import pandas as pd


class Restaurant:
    def __init__(self):
        self.restaurants = pd.read_csv(
            "resources/attributes/Restaurants.csv",
            converters={"location": self.create_point}
        )

    @staticmethod
    def create_point(col: str):
        point_tpl = ()
        if col.startswith("POINT"):
            for point in re.finditer("[-]*\d+\.\d*\s[-]*\d+\.\d*", col, re.IGNORECASE):
                x, y = point.group().split(" ")
                point_tpl = (float(x), float(y))
        return point_tpl

    def get_points(self):
        return [(int(self.restaurants["restaurantId"].iloc[i]), point, self.restaurants["maxOccupancy"].iloc[i])
                for point, i in zip(self.restaurants["location"], range(len(self.restaurants["location"])))]
