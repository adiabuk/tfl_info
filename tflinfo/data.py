#!/usr/bin/env python
#pylint: disable=wrong-import-position,wrong-import-order,try-except-raise
"""
Class for manipulating data from TFL API
"""
import functools
import json
from math import radians, sin, cos, acos
from urllib.parse import urlencode
import requests
import warnings
warnings.filterwarnings("ignore")  # disable pandas warning on OSX
import pandas as pd

class Bikes():
    """
    Fetch/Hold/Manipulate data from tfl API
    """
    def __init__(self, app_id, app_key):
        params = urlencode({'app_id':app_id, 'app_key':app_key})
        api = requests.get('https://api.tfl.gov.uk/bikePoint?'+ params)

        # API returns a 200 with invalid credentials so need to scrape for the error in the HTML
        if "you must have a valid application ID and key" in api.text:
            raise PermissionError("Invalid credentials")
        #print(api.text)
        try:
            self.api = self.deserialize(api.text)
        except json.JSONDecodeError:
            raise

    @staticmethod
    def deserialize(string):
        """
        deserialize string to dict and flatten lists to enable easy referencing
        """
        #  deserialize string
        text = json.loads(string)

        # flatten top level of object
        flat = {item['id']:item for item in text}

        # traverse tree to find flatten-able object
        # cast to list to avoid RuntimeError-dict size changed
        for top_key, top_val in  list(flat.items()):   # top level of dict
            for item_key, item_val in list(top_val.items()):  # second level
                if item_key == 'additionalProperties':  # list
                    for additional_item in item_val:
                        current_name = additional_item["key"]
                        # create dict items from list of additional properties
                        flat[top_key][current_name] = additional_item
                    # remove old list from structure
                    del flat[top_key]['additionalProperties']
        return flat

    @staticmethod
    def left_justified(dframe):
        """
        Left justify pandas dataframe columns
        """
        formatters = {}
        for col in list(dframe.columns):
            max_length = dframe[col].str.len().max()
            form = "{{:<{}s}}".format(max_length)
            formatters[col] = functools.partial(str.format, form)
        return dframe.to_string(formatters=formatters, index=False, justify="left")

    @staticmethod
    def get_distance(start_lat, start_lon, fin_lat, fin_lon):
        """
        get difference between 2 coordinates in metres using haversine formula
        return float rounded to 1dp
        """
        start_lat = radians(start_lat)
        start_lon = radians(start_lon)
        fin_lat = radians(fin_lat)
        fin_lon = radians(fin_lon)

        result = (6371e3 * acos(sin(start_lat) * sin(fin_lat) +
                                cos(start_lat) * cos(fin_lat) *
                                cos(start_lon - fin_lon)))
        return round(result, 1)

    def distance_search(self, *args):
        """
        Search for bike points within a given distance from given co-ords
        """
        results = []
        for value in self.api.values():
            try:
                # turn all args into floats
                start_lat, start_lon, max_dist = [float(i) for i in args]
            except ValueError:
                # Invalid Values passed
                return None

            fin_lat = value['lat']
            fin_lon = value['lon']
            dist = self.get_distance(start_lat, start_lon, fin_lat, fin_lon)

            if dist < max_dist:
                results.append(self.stringify_list(((value['id']), value['commonName'],
                                                    value['lat'], value['lon'], dist)))
        columns = self.spacify_list(['Id', 'Name', 'Latitude', 'Longitude', 'Distance'])
        dframe = pd.DataFrame(results, columns=columns)

        return self.left_justified(dframe) if not dframe.empty else ""

    @staticmethod
    def spacify_list(lst):
        """
        Add leading space for each item in list to properly align dataframe column names
        """
        return [' ' + i for i in lst]

    @staticmethod
    def stringify_list(lst):
        """
        Turn each item in list into a string
        """
        return [str(i) for i in lst]

    def get_id(self, *args):
        """
        Get details of bike point from a given ID
        """
        results = []
        try:
            record = self.api[args[0]]
        except KeyError:
            return None

        results.append(self.stringify_list((record['commonName'], record['lat'], record['lon'],
                                            record['NbBikes']['value'],
                                            record['NbEmptyDocks']['value'])))
        columns = self.spacify_list(['Name', 'Latitude', 'Longitude', 'Num Bikes', 'Empty Docks'])
        dframe = pd.DataFrame(results, columns=columns)

        return self.left_justified(dframe) if not dframe.empty else ""

    def search(self, *args):
        """
        Search for bikepoint using part of name
        """
        results = []

        for key, value in self.api.items():
            if args[0] in value['commonName']:
                results.append(self.stringify_list((key, value['commonName'],
                                                    value['lat'], value['lon'])))

        columns = self.spacify_list(['Id', 'Name', 'Latitude', 'Longitude'])
        dframe = pd.DataFrame(results, columns=columns)
        return self.left_justified(dframe) if not dframe.empty else ""
