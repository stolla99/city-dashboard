import itertools
import re

import plotly
import plotly.express.colors as colors

import numpy as np
import pandas as pd

from apartments import Apartment


def append_tuple(lst, point):
    lst[0].append(point[0])
    lst[1].append(point[1])
    return 0


def extend_tuple(lst, point):
    lst[0].extend(point[0])
    lst[1].extend(point[1])
    return 0


class Building:
    def __init__(self):
        self.bounds = {"min_x": np.inf, "max_x": np.NINF, "min_y": np.inf, "max_y": np.NINF}
        self.buildings = pd.read_csv(
            "resources/attributes/Buildings.csv",
            converters={"location": self.create_polygon, "units": self.create_list})
        self.average_rental_cost = []

    def create_polygon(self, col: str):
        point_list = []
        if col.startswith("POLYGON"):
            for polygon in re.finditer("[-]*\d+\.\d*\s[-]*\d+\.\d*", col, re.IGNORECASE):
                x, y = polygon.group().split(" ")
                self.bounds["min_x"] = min(self.bounds["min_x"], float(x))
                self.bounds["min_y"] = min(self.bounds["min_y"], float(y))
                self.bounds["max_x"] = max(self.bounds["max_x"], float(x))
                self.bounds["max_y"] = max(self.bounds["max_y"], float(y))
                point_list.append((float(x), float(y)))
        return point_list

    def get_color_dict(self):
        return {"Residential": "#e76f51", "Commercial": "#2a9d8f", "School": "#264653"}

    def create_list(self, col):
        units_list = []
        for unit in re.finditer("[0-9]+", col, re.IGNORECASE):
            units_list.append(int(unit.group()))
        return units_list

    def get_x_y_bounds(self):
        return [self.bounds["min_x"], self.bounds["max_x"]], [self.bounds["max_y"], self.bounds["min_y"]]

    def get_building_with_key(self, _key):
        if _key == "Residential":
            _key = "Residental"
        return self.buildings[self.buildings["buildingType"] == _key]["buildingId"].tolist()

    def get_occupancy_with_key(self, _key):
        if _key == "Residential":
            _key = "Residental"
        return self.buildings[self.buildings["maxOccupancy"] == _key]["maxOccupancy"].tolist()

    def compute_polygon(self):
        building_dict = {"Residential": ([], []), "Commercial": ([], []), "School": ([], [])}
        for poly, i in zip(self.buildings["location"], range(len(self.buildings["location"]))):
            x_lst = []
            y_lst = []
            if len(poly) >= 3:
                for (x, y), i in zip(poly, range(len(poly))):
                    x_lst.append(x)
                    y_lst.append(y)
                x_lst.append(None)
                y_lst.append(None)
                match str(self.buildings["buildingType"][i]):
                    case "Residental":
                        building_dict["Residential"][0].extend(x_lst)
                        building_dict["Residential"][1].extend(y_lst)
                    case "Commercial":
                        building_dict["Commercial"][0].extend(x_lst)
                        building_dict["Commercial"][1].extend(y_lst)
                    case "School":
                        building_dict["School"][0].extend(x_lst)
                        building_dict["School"][1].extend(y_lst)
                    case _:
                        building_dict["Residential"][0].extend(x_lst)
                        building_dict["Residential"][1].extend(y_lst)
        return building_dict

    def polygon_generator(self, apt: Apartment):
        self.average_rental_cost = []
        mapped_coords = {"Residential": [], "Commercial": [], "School": []}
        building_shells = {"Residential": ([], []), "Commercial": ([], []), "School": ([], [])}
        building_holes = {"Residential": ([], []), "Commercial": ([], []), "School": ([], [])}
        for poly, bld_type, bld_id in zip(self.buildings["location"],
                                          self.buildings["buildingType"],
                                          self.buildings["buildingId"]):
            bld_id_tpl = []
            shells = ([], [])
            holes = ([], [])
            add_to_shell = True
            if len(poly) >= 3:
                first = poly[0]
                for point, j in zip(poly, range(len(poly))):
                    if j > 1 and first == point:
                        add_to_shell = False
                        append_tuple(shells, point)
                        bld_id_tpl.append(bld_id)
                        continue
                    if add_to_shell:
                        append_tuple(shells, point)
                        bld_id_tpl.append(bld_id)
                    else:
                        append_tuple(holes, point)
            if len(holes[0]) > 0:
                if holes[0][-1] is not None:
                    append_tuple(holes, (None, None))
            if len(shells[0]) > 0:
                if shells[0][-1] is not None:
                    append_tuple(shells, (None, None))
                    bld_id_tpl.append(None)
            match str(bld_type):
                case "Residental":
                    extend_tuple(building_shells["Residential"], shells)
                    extend_tuple(building_holes["Residential"], holes)
                    mapped_coords["Residential"].extend(bld_id_tpl)
                    units = self.buildings[self.buildings["buildingId"] == bld_id]["units"].tolist()[0]

                    if units:
                        avg = np.average(apt.apartments[apt.apartments["apartmentId"].isin(units)]["rentalCost"])
                        x = colors.PLOTLY_SCALES["Viridis"]
                        low = apt.apartments["rentalCost"].min()
                        high = apt.apartments["rentalCost"].max()
                        c = colors.sample_colorscale(x,
                                                     samplepoints=[(avg - low) / (high - low)])
                        self.average_rental_cost.append((bld_id, avg, c[0]))
                    else:
                        self.average_rental_cost.append((bld_id, 0.0, "#bcb8b1"))
                case "Commercial":
                    extend_tuple(building_shells["Commercial"], shells)
                    extend_tuple(building_holes["Commercial"], holes)
                    mapped_coords["Commercial"].extend(bld_id_tpl)
                case "School":
                    extend_tuple(building_shells["School"], shells)
                    extend_tuple(building_holes["School"], holes)
                    mapped_coords["School"].extend(bld_id_tpl)
        return building_shells, building_holes, mapped_coords

    def single_polygon_generator_(self, _building_id):
        poly = self.buildings[self.buildings["buildingId"] == _building_id]["location"].tolist()[0]
        shells = ([], [])
        holes = ([], [])
        add_to_shell = True
        if len(poly) >= 3:
            first = poly[0]
            for point, j in zip(poly, range(len(poly))):
                if j > 1 and first == point:
                    add_to_shell = False
                    append_tuple(shells, point)
                    continue
                if add_to_shell:
                    append_tuple(shells, point)
                else:
                    append_tuple(holes, point)
        return shells, holes
