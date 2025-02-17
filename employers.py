import re

import pandas as pd


class Employers:
    def __init__(self):
        self.employers = pd.read_csv(
            "resources/attributes/Employers.csv",
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
        rest_list = []
        for point, i in zip(self.employers["location"], range(len(self.employers["location"]))):
            if point != ():
                rest_list.append((int(self.employers["employerId"].iloc[i]), point))
        return rest_list
