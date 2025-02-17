import re

import pandas as pd


class Pubs:
    def __init__(self):
        self.pubs = pd.read_csv(
            "resources/attributes/Pubs.csv",
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
        return [(int(self.pubs["pubId"].iloc[i]), point, self.pubs["maxOccupancy"].iloc[i])
                for point, i in zip(self.pubs["location"], range(len(self.pubs["location"])))]