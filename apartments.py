import re

import pandas as pd


class Apartment:
    def __init__(self):
        self.apartments = pd.read_csv(
            "resources/attributes/Apartments.csv",
            converters={"location": self.create_point}
        )

    def create_point(self, col: str):
        point_tpl = ()
        if col.startswith("POINT"):
            for point in re.finditer("[-]*\d+\.\d*\s[-]*\d+\.\d*", col, re.IGNORECASE):
                x, y = point.group().split(" ")
                point_tpl = (float(x), float(y))
        return point_tpl

    def get_points(self):
        return [(int(self.apartments["apartmentId"].iloc[i]), point, self.apartments["rentalCost"].iloc[i])
                for point, i in zip(self.apartments["location"], range(len(self.apartments["location"])))]
