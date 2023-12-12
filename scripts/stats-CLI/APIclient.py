import requests
import numpy as np
import json
import datetime
from datetime import date

# create class for managing stats queried from Invenio API response

class APIclient():
    # constructor: an APIResponse object keeps track of headers for the API request, the JSON response from
    # the records endpoint, and a dictionary mapping id->deposit info
    def __init__(self, bearer_token):
        self.bearer = 'Bearer ' + bearer_token
        self.headers = {'Content-Type': 'application/json', 'Authorization': self.bearer, 'Cookie': 
                        'csrftoken=eyJhbGciOiJIUzUxMiIsImlhdCI6MTcwMTExODQ1MiwiZXhwIjoxNzAxMjA0ODUyfQ.IlRrNl \
                        NSNmVwcUJCYUpaQjBWSDVzT05uNDFLQzBYUWE1Ig.nMPrX2GdhkAaBJU-d2ORvWp7qIIpw6hSTqi-oY6rgHK \
                        WKZxNHX8biGyycs_I43hfSouy4LgTpni4CQg0bGKPlg'
                        }
        self.payload = None
        self.records = None
        self.stats = None
        self.deposits = {}
        self.records_url = 'https://invenio-dev.hcommons-staging.org/api/records'
        self.stats_url = 'https://invenio-dev.hcommons-staging.org/api/stats'
        # self.depositID = []


    # function that returns JSON string from a GET request to records endpoint
    # also creates dictionary mapping deposit ID to dictionary of deposit info (from records endpoint)
    def get_records(self):
        # .json() turns the JSON string into a python dictionary
        self.records = requests.get(self.records_url, headers=self.headers, verify=False).json()
        # create the dictionary
        for item in self.records['hits']['hits']:
            id = item['id']
            self.deposits[id] = item
        # create list of dictionaries of deposit recids and parent_recids
        #for item in self.records['hits']['hits']:
            
    
    def get_stats(self, type, id, version, start_date, end_date):
        if type == 'views':
            if version.lower() == "current":
                self.payload = json.dumps({"views": {"stat": "record-view", "params": {"start_date": start_date, 
                                                                                       "end_date": end_date, "recid": id}}})
            else:
                # id needs to be the parent_recid
                self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                     "params": {"start_date": start_date, "end_date": end_date, "parent_recid": id}}})
            self.stats = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
        else:
            if version.lower() == "current":
                self.payload = json.dumps({"views": {"stat": "record-download", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, "recid": id}}})
            else:
                # id needs to be the parent_recid
                self.payload = json.dumps({"views": {"stat": "record-download-all-versions", "params": {"start_date": start_date, 
                                                                                       "end_date": end_date, "parent_recid": id}}})
            self.stats = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()

    """
    def get_stats_time_range(self, type, id, start_date, end_date):
        if type == 'views':
            self.payload = json.dumps({"views": {"stat": "record-view", "params": {"start_date": start_date, 
                                                                                   "end_date": end_date, "recid": id}}})
            self.stats = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
        else:
            self.payload = json.dumps({"views": {"stat": "record-download", "params": {"start_date": start_date, 
                                                                                   "end_date": end_date, "recid": id}}})
            self.stats = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
    """

    # function that returns the number of deposits, either over time or total
    def total_deposits(self, freq):
        if self.records == None:
            self.get_records()

        # might need to do time sorting for dictionaries returned?
        if freq.lower() == 'monthly':
            time_dict = {}
            for key in self.deposits:
                remove_time = self.deposits[key]['created'].split('T')
                y_m_d = remove_time[0].split('-')
                month_year = y_m_d[0] + '-' + y_m_d[1] 
                time_dict[month_year] = time_dict.get(month_year, 0) + 1
            return time_dict
        
        elif freq.lower() == 'daily':
            time_dict = {}
            for key in self.deposits:
                remove_time = self.deposits[key]['created'].split('T')
                y_m_d = remove_time[0]
                time_dict[y_m_d] = time_dict.get(y_m_d, 0) + 1
            return time_dict
        
        # weekly: isocalendar() from datetime.time
        elif freq.lower() == 'weekly':
            time_dict = {}
            for key in self.deposits:
                remove_time = self.deposits[key]['created'].split('T')
                y_m_d = remove_time[0].split('-')
                date_tuple = datetime.date(int(y_m_d[0]), int(y_m_d[1]), int(y_m_d[2]))
                year = date_tuple.isocalendar()[0]
                week = date_tuple.isocalendar()[1]
                week_str = 'Week ' + str(week) + ', ' + str(year)
                time_dict[week_str] = time_dict.get(week_str, 0) + 1
            return time_dict

        else:
            return self.records['hits']['total']
        
    
    # function that returns the total num of views of a deposit
    def total_views(self, id, version, start_date, end_date, unique):
        if id == 'all':
            self.get_records()
            views_dict = {}
            for key in self.deposits:
                if version.lower() == "current" and unique:
                    views_dict[key] = self.deposits[key]['stats']['this_version']['unique_views']
                elif version.lower() == "current" and not unique:
                    views_dict[key] = self.deposits[key]['stats']['this_version']['views']
                elif version.lower() == "all" and unique:
                    views_dict[key] = self.deposits[key]['stats']['all_versions']['unique_views']
                else:
                    views_dict[key] = self.deposits[key]['stats']['all_versions']['views']
            return views_dict
        else:
            self.get_stats('views', id, version, start_date, end_date)
            if unique:
                return self.stats["views"]["unique_views"]
            return self.stats["views"]["views"]


    # function that returns the average num of views across all deposits (can handle over time)
    def avg_views(self, version, unique):
        if self.records == None:
            self.get_records()

        total_views = 0
        for key in self.deposits:
            if version.lower() == "current" and unique == True:
                no_views = self.deposits[key]['stats']['this_version']['unique_views']
                total_views += no_views
            elif version.lower() == "current" and unique == False:
                no_views = self.deposits[key]['stats']['this_version']['views']
                total_views += no_views
            elif version.lower() == "all" & unique == True:
                no_views = self.deposits[key]['stats']['all_versions']['unique_views']
                total_views += no_views
            else:
                no_views = self.deposits[key]['stats']['all_versions']['views']
                total_views += no_views
        
        total_deposits = self.records['hits']['total']
        return total_views / total_deposits
    
    
    # function that returns the total num of downloads of a deposit
    def total_downloads(self, id, version, start_date, end_date, unique):
        if id == 'all':
            self.get_records()
            downloads_dict = {}
            for key in self.deposits:
                if version.lower() == "current" and unique:
                    downloads_dict[key] = self.deposits[key]['stats']['this_version']['unique_downloads']
                elif version.lower() == "current" and not unique:
                    downloads_dict[key] = self.deposits[key]['stats']['this_version']['downloads']
                elif version.lower() == "all" and unique:
                    downloads_dict[key] = self.deposits[key]['stats']['all_versions']['unique_downloads']
                else:
                    downloads_dict[key] = self.deposits[key]['stats']['all_versions']['downloads']
            return downloads_dict
        else:
            self.get_stats('downloads', id, version, start_date, end_date)
            if unique:
                return self.stats["views"]["unique_downloads"]
            return self.stats["views"]["downloads"]
        

    # function that returns the average num of downloads across all deposits (can handle over time)
    def avg_downloads(self, version, unique):
        if self.records == None:
            self.get_records()

        total_downloads = 0
        for key in self.deposits:
            if version.lower() == "current" and unique == True:
                no_downloads = self.deposits[key]['stats']['this_version']['unique_downloads']
                total_downloads += no_downloads
            elif version.lower() == "current" and unique == False:
                no_views = self.deposits[key]['stats']['this_version']['downloads']
                total_downloads += no_downloads
            elif version.lower() == "all" & unique == True:
                no_views = self.deposits[key]['stats']['all_versions']['unique_downloads']
                total_downloads += no_downloads
            else:
                no_views = self.deposits[key]['stats']['all_versions']['downloads']
                total_downloads += no_downloads
        
        total_deposits = self.records['hits']['total']
        return total_downloads / total_deposits
        

    # return a dictionary of deposits and number of downloads, sorted
    def top_downloads(self):
        if self.records == None:
            self.get_records()
        
        downloads = self.total_downloads('all')
        keys = list(downloads.keys())
        values = list(downloads.values())
        sorted_indices = np.argsort(values)
        sorted_dict = {keys[i]: values[i] for i in sorted_indices}
        return sorted_dict
