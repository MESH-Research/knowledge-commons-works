import requests
import numpy as np
import json
import calendar
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
        # self.stats = None
        self.deposits = {}
        # self.depositIDs = {}
        self.records_url = 'https://invenio-dev.hcommons-staging.org/api/records'
        self.stats_url = 'https://invenio-dev.hcommons-staging.org/api/stats'


    # function that returns JSON string from a GET request to records endpoint
    # also creates dictionary mapping deposit ID to dictionary of deposit info (from records endpoint)
    def get_records(self, version):
        # .json() turns the JSON string into a python dictionary
        self.records = requests.get(self.records_url, headers=self.headers, verify=False).json()
        # create the dictionary
        for item in self.records['hits']['hits']:
            if version == 'current':
                id = item['id']
            else:
                id = item['parent']['id']
            self.deposits[id] = item
            

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
    def total_views(self, id, version, start_date, end_date, freq, unique):
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
            if freq == None:
                if version.lower() == "current":
                    self.payload = json.dumps({"views": {"stat": "record-view", "params": {"start_date": start_date, 
                                                                                       "end_date": end_date, "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                     "params": {"start_date": start_date, "end_date": end_date, "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    return response["views"]["unique_views"]
                return response["views"]["views"]
            
            else:
                views_over_time = {}
                start_y_m_d = start_date.split("-")
                start_year = int(start_y_m_d[0])
                start_month = int(start_y_m_d[1].lstrip('0'))
                start_day = int(start_y_m_d[2])
                end_y_m_d = end_date.split("-")
                end_year = int(end_y_m_d[0])
                end_month = int(end_y_m_d[1].lstrip('0'))
                end_day = int(end_y_m_d[2])
                start_datetime = datetime.date(start_year, start_month, start_day)
                end_datetime = datetime.date(end_year, end_month, end_day)

                if freq.lower() == "monthly":
                    month_num = start_datetime.month
                    if month_num < 10:
                        month_str = "0" + str(month_num)
                    else:
                        month_str = str(month_num)
                    num_days = calendar.monthrange(start_year, month_num)[1]
                    last_mo_day = datetime.date(start_year, month_num, num_days)
                    if version.lower() == "current":
                        self.payload = json.dumps({"views": {"stat": "record-view", 
                                                            "params": {"start_date": start_date, 
                                                                        "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                        "recid": id}}})
                    else:
                        # id needs to be the parent_recid
                        self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                    "params": {"start_date": start_date, 
                                                               "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    date_key = month_str + "-" + str(start_year)
                    if unique:
                        views_over_time[date_key] = response["views"]["unique_views"]
                    else:
                        views_over_time[date_key] = response["views"]["views"]
                    date_holder = last_mo_day + datetime.timedelta(days=1)

                    while date_holder <= end_datetime:
                        month_num = date_holder.month
                        year_num = date_holder.year
                        if month_num < 10:
                            month_str = "0" + str(month_num)
                        else:
                            month_str = str(month_num)

                        if date_holder.month == end_datetime.month and date_holder.year == end_datetime.year:
                            if version.lower() == "current":
                                self.payload = json.dumps({"views": {"stat": "record-view", 
                                                                     "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                                "end_date": end_date, "recid": id}}})
                            else:
                                # id needs to be the parent_recid
                                self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                        "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                   "end_date": end_date, 
                                                                    "parent_recid": id}}})
                            response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                            date_key = month_str + "-" + str(year_num)
                            if unique:
                                views_over_time[date_key] = response["views"]["unique_views"]
                            else:
                                views_over_time[date_key] = response["views"]["views"]
                            
                            return views_over_time

                        else:        
                            num_days = calendar.monthrange(year_num, month_num)[1]
                            last_mo_day = datetime.date(year_num, month_num, num_days)
                            if version.lower() == "current":
                                self.payload = json.dumps({"views": {"stat": "record-view", 
                                                                     "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                                "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                                "recid": id}}})
                            else:
                                # id needs to be the parent_recid
                                self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                            "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                       "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                        "parent_recid": id}}})
                            response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                            date_key = month_str + "-" + str(year_num)
                            if unique:
                                views_over_time[date_key] = response["views"]["unique_views"]
                            else:
                                views_over_time[date_key] = response["views"]["views"]
                        date_holder = last_mo_day + datetime.timedelta(days=1)
                
                elif freq.lower() == "weekly":
                    day_of_week = start_datetime.weekday()
                    if day_of_week == 6:
                        init_delta = datetime.timedelta(days=6)
                    else:
                        init_delta = datetime.timedelta(days=5-day_of_week)
                    start_week = start_datetime
                    end_week = start_datetime + init_delta
                    delta = datetime.timedelta(days=6)

                    while (start_week <= end_datetime):

                        if version.lower() == "current":
                            self.payload = json.dumps({"views": {"stat": "record-view", 
                                                    "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                                "end_date": (end_datetime.strftime("%Y-%m-%d") 
                                                                             if end_week > end_datetime else end_week.strftime("%Y-%m-%d")), 
                                                                "recid": id}}})
                        else:
                            self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                    "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                                "end_date": (end_datetime.strftime("%Y-%m-%d") 
                                                                             if end_week > end_datetime else end_week.strftime("%Y-%m-%d")), 
                                                                "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        date_key = "Week of " + start_week.strftime("%Y-%m-%d") + " - " + \
                                    (end_datetime.strftime("%Y-%m-%d") if end_week > end_datetime else end_week.strftime("%Y-%m-%d"))
                        
                        if unique:
                            views_over_time[date_key] = response["views"]["unique_views"]
                        else:
                            views_over_time[date_key] = response["views"]["views"]
                        
                        start_week = end_week + datetime.timedelta(days=1)
                        end_week = start_week + delta
                    
                    return views_over_time
                
                else:
                    delta = datetime.timedelta(days=1)
                    
                    while (start_datetime <= end_datetime):
                        if version.lower() == "current":
                            self.payload = json.dumps({"views": {"stat": "record-view", 
                                                        "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                   "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                    "recid": id}}})
                        else:
                            self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                        "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                   "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                    "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        if unique:
                            views_over_time[start_datetime.strftime("%Y-%m-%d")] = response["views"]["unique_views"]
                        else:
                            views_over_time[start_datetime.strftime("%Y-%m-%d")] = response["views"]["views"]
                        start_datetime += delta

                    return views_over_time


    # function that returns the average num of views across all deposits (can handle over time)
    def avg_views(self, version, start_date, end_date, freq, unique):
        if self.records == None:
            self.get_records(version)
        
        total_deposits = self.records['hits']['total']

        if freq == None and start_date == None and end_date == None:
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
            return total_views / total_deposits
        
        elif freq == None and start_date != None and end_date != None:
            total_views = 0
            for id in self.deposits:
                if version.lower() == "current" and unique == True:
                    self.payload = json.dumps({"views": {"stat": "record-view", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    no_views = response['stats']['this_version']['unique_views']
                    total_views += no_views
                elif version.lower() == "current" and unique == False:
                    self.payload = json.dumps({"views": {"stat": "record-view", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    no_views = response['stats']['this_version']['views']
                    total_views += no_views
                elif version.lower() == "all" & unique == True:
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    no_views = response['stats']['all_versions']['unique_views']
                    total_views += no_views
                else:
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    no_views = response['stats']['all_versions']['views']
                    total_views += no_views

            return total_views / total_deposits
        
        elif freq.lower() == "monthly" and start_date != None and end_date != None:
            avg_views = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)

            month_num = start_datetime.month
            if month_num < 10:
                month_str = "0" + str(month_num)
            else:
                month_str = str(month_num)
            num_days = calendar.monthrange(start_year, month_num)[1]
            last_mo_day = datetime.date(start_year, month_num, num_days)

            num_views = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"views": {"stat": "record-view", 
                                                        "params": {"start_date": start_date, 
                                                                    "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                "params": {"start_date": start_date, 
                                                            "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_views += response["views"]["unique_views"]
                else:
                    num_views += response["views"]["views"]
            
            date_key = month_str + "-" + str(start_year)
            avg_views[date_key] = num_views / total_deposits

            date_holder = last_mo_day + datetime.timedelta(days=1)

            while date_holder <= end_datetime:
                num_views = 0
                month_num = date_holder.month
                year_num = date_holder.year
                if month_num < 10:
                    month_str = "0" + str(month_num)
                else:
                    month_str = str(month_num)

                if date_holder.month == end_datetime.month and date_holder.year == end_datetime.year:
                    for id in self.deposits:
                        if version.lower() == "current":
                            self.payload = json.dumps({"views": {"stat": "record-view", 
                                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                            "end_date": end_date, "recid": id}}})
                        else:
                            # id needs to be the parent_recid
                            self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                "end_date": end_date, 
                                                                "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        if unique:
                            num_views += response["views"]["unique_views"]
                        else:
                            num_views += response["views"]["views"]
            
                    date_key = month_str + "-" + str(start_year)
                    avg_views[date_key] = num_views / total_deposits
                    
                    return avg_views

                else:        
                    num_days = calendar.monthrange(year_num, month_num)[1]
                    last_mo_day = datetime.date(year_num, month_num, num_days)
                    for id in self.deposits:
                        if version.lower() == "current":
                            self.payload = json.dumps({"views": {"stat": "record-view", 
                                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                            "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                            "recid": id}}})
                        else:
                            # id needs to be the parent_recid
                            self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                        "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                    "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                    "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        if unique:
                            num_views += response["views"]["unique_views"]
                        else:
                            num_views += response["views"]["views"]
                
                    date_key = month_str + "-" + str(start_year)
                    avg_views[date_key] = num_views / total_deposits
                    date_holder = last_mo_day + datetime.timedelta(days=1)

        elif freq.lower() == "weekly" and start_date != None and end_date != None:
            avg_views = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)
            day_of_week = start_datetime.weekday()
            if day_of_week == 6:
                init_delta = datetime.timedelta(days=6)
            else:
                init_delta = datetime.timedelta(days=5-day_of_week)
            start_week = start_datetime
            end_week = start_datetime + init_delta
            delta = datetime.timedelta(days=6)

            while (start_week <= end_datetime):
                num_views = 0
                for id in self.deposits:
                    if version.lower() == "current":
                        self.payload = json.dumps({"views": {"stat": "record-view", 
                                                "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                            "end_date": (end_datetime.strftime("%Y-%m-%d") 
                                                                            if end_week > end_datetime else end_week.strftime("%Y-%m-%d")), 
                                                            "recid": id}}})
                    else:
                        self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                            "end_date": (end_datetime.strftime("%Y-%m-%d") 
                                                                            if end_week > end_datetime else end_week.strftime("%Y-%m-%d")), 
                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        num_views += response["views"]["unique_views"]
                    else:
                        num_views += response["views"]["views"]

                date_key = "Week of " + start_week.strftime("%Y-%m-%d") + " - " + \
                            (end_datetime.strftime("%Y-%m-%d") if end_week > end_datetime else end_week.strftime("%Y-%m-%d"))
                avg_views[date_key] = num_views / total_deposits
                start_week = end_week + datetime.timedelta(days=1)
                end_week = start_week + delta
            
            return avg_views
        
        elif freq.lower() == "daily" and start_date != None and end_date != None:
            avg_views = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)
            delta = datetime.timedelta(days=1)
                    
            while (start_datetime <= end_datetime):
                num_views = 0
                for id in self.deposits:
                    if version.lower() == "current":
                        self.payload = json.dumps({"views": {"stat": "record-view", 
                                                    "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "recid": id}}})
                    else:
                        self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                    "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        num_views += response["views"]["unique_views"]
                    else:
                        num_views += response["views"]["views"]

                avg_views[start_datetime.strftime("%Y-%m-%d")] = num_views / total_deposits
                start_datetime += delta

            return avg_views

    
    # function that returns the total num of downloads of a deposit
    def total_downloads(self, id, version, start_date, end_date, freq, unique):
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
            downloads_over_time = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)

            if freq.lower() == "monthly":
                month_num = start_datetime.month
                if month_num < 10:
                    month_str = "0" + str(month_num)
                else:
                    month_str = str(month_num)
                num_days = calendar.monthrange(start_year, month_num)[1]
                last_mo_day = datetime.date(start_year, month_num, num_days)
                if version.lower() == "current":
                            self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                        "params": {"start_date": start_date, 
                                                                    "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": start_date, 
                                                            "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                date_key = month_str + "-" + str(start_year)
                if unique:
                    downloads_over_time[date_key] = response["downloads"]["unique_downloads"]
                else:
                    downloads_over_time[date_key] = response["downloads"]["downloads"]
                date_holder = last_mo_day + datetime.timedelta(days=1)

                while date_holder <= end_datetime:
                    month_num = date_holder.month
                    year_num = date_holder.year
                    if month_num < 10:
                        month_str = "0" + str(month_num)
                    else:
                        month_str = str(month_num)

                    if date_holder.month == end_datetime.month and date_holder.year == end_datetime.year:
                        if version.lower() == "current":
                            self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                            "end_date": end_date, "recid": id}}})
                        else:
                            # id needs to be the parent_recid
                            self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                "end_date": end_date, 
                                                                "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        date_key = month_str + "-" + str(year_num)
                        if unique:
                            downloads_over_time[date_key] = response["downloads"]["unique_downloads"]
                        else:
                            downloads_over_time[date_key] = response["downloads"]["downloads"]
                        
                        return downloads_over_time

                    else:        
                        num_days = calendar.monthrange(year_num, month_num)[1]
                        last_mo_day = datetime.date(year_num, month_num, num_days)
                        if version.lower() == "current":
                            self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                            "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                            "recid": id}}})
                        else:
                            # id needs to be the parent_recid
                            self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                        "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                    "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                    "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        date_key = month_str + "-" + str(year_num)
                        if unique:
                            downloads_over_time[date_key] = response["downloads"]["unique_downloads"]
                        else:
                            downloads_over_time[date_key] = response["downloads"]["downloads"]
                    date_holder = last_mo_day + datetime.timedelta(days=1)
            
            elif freq.lower() == "weekly":
                day_of_week = start_datetime.weekday()
                if day_of_week == 6:
                    init_delta = datetime.timedelta(days=6)
                else:
                    init_delta = datetime.timedelta(days=5-day_of_week)
                start_week = start_datetime
                end_week = start_datetime + init_delta
                delta = datetime.timedelta(days=6)

                while (start_week <= end_datetime):
                    
                    if version.lower() == "current":
                        self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                            "end_date": (end_datetime.strftime("%Y-%m-%d") if end_week > end_datetime \
                                                                         else end_week.strftime("%Y-%m-%d")), 
                                                            "recid": id}}})
                    else:
                        self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                            "end_date": (end_datetime.strftime("%Y-%m-%d") if end_week > end_datetime \
                                                                         else end_week.strftime("%Y-%m-%d")), 
                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    date_key = "Week of " + start_week.strftime("%Y-%m-%d") + " - " + (end_datetime.strftime("%Y-%m-%d") if end_week > end_datetime \
                                                                                           else end_week.strftime("%Y-%m-%d"))
                    #print(response)
                    if unique:
                        downloads_over_time[date_key] = response["downloads"]["unique_downloads"]
                    else:
                        downloads_over_time[date_key] = response["downloads"]["downloads"]

                    start_week = end_week + datetime.timedelta(days=1)
                    end_week = start_week + delta
                
                return downloads_over_time
            
            else:
                delta = datetime.timedelta(days=1)
                
                while (start_datetime <= end_datetime):
                    if version.lower() == "current":
                        self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                    "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                               "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "recid": id}}})
                    else:
                        self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                    "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                               "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        downloads_over_time[start_datetime.strftime("%Y-%m-%d")] = response["downloads"]["unique_downloads"]
                    else:
                        downloads_over_time[start_datetime.strftime("%Y-%m-%d")] = response["downloads"]["downloads"]
                    start_datetime += delta

                return downloads_over_time
        

    # function that returns the average num of downloads across all deposits (can handle over time)
    def avg_downloads(self, version, start_date, end_date, freq, unique):
        if self.records == None:
            self.get_records(version)
        
        total_deposits = self.records['hits']['total']

        if freq == None and start_date == None and end_date == None:
            total_downloads = 0
            for key in self.deposits:
                if version.lower() == "current" and unique == True:
                    total_downloads += self.deposits[key]['stats']['this_version']['unique_downloads']
                elif version.lower() == "current" and unique == False:
                    total_downloads += self.deposits[key]['stats']['this_version']['downloads']
                elif version.lower() == "all" & unique == True:
                    total_downloads += self.deposits[key]['stats']['all_versions']['unique_downloads']
                else:
                    total_downloads += self.deposits[key]['stats']['all_versions']['downloads']
            return total_downloads / total_deposits
        
        elif freq == None and start_date != None and end_date != None:
            total_downloads = 0
            for id in self.deposits:
                if version.lower() == "current" and unique == True:
                    self.payload = json.dumps({"downloads": {"stat": "record-download", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    total_downloads += response['stats']['this_version']['unique_downloads']
                elif version.lower() == "current" and unique == False:
                    self.payload = json.dumps({"downloads": {"stat": "record-download", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    total_downloads += response['stats']['this_version']['downloads']
                elif version.lower() == "all" & unique == True:
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    total_downloads += response['stats']['this_version']['unique_downloads']
                else:
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", "params": {"start_date": start_date, 
                                                                                            "end_date": end_date, 
                                                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    total_downloads += response['stats']['this_version']['downloads']

            return total_downloads / total_deposits
        
        elif freq.lower() == "monthly" and start_date != None and end_date != None:
            avg_downloads = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)

            month_num = start_datetime.month
            if month_num < 10:
                month_str = "0" + str(month_num)
            else:
                month_str = str(month_num)
            num_days = calendar.monthrange(start_year, month_num)[1]
            last_mo_day = datetime.date(start_year, month_num, num_days)

            num_downloads = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                        "params": {"start_date": start_date, 
                                                                    "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": start_date, 
                                                            "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_downloads += response["downloads"]["unique_downloads"]
                else:
                    num_downloads += response["downloads"]["downloads"]
            
            date_key = month_str + "-" + str(start_year)
            avg_downloads[date_key] = num_downloads / total_deposits

            date_holder = last_mo_day + datetime.timedelta(days=1)

            while date_holder <= end_datetime:
                num_downloads = 0
                month_num = date_holder.month
                year_num = date_holder.year
                if month_num < 10:
                    month_str = "0" + str(month_num)
                else:
                    month_str = str(month_num)

                if date_holder.month == end_datetime.month and date_holder.year == end_datetime.year:
                    for id in self.deposits:
                        if version.lower() == "current":
                            self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                            "end_date": end_date, "recid": id}}})
                        else:
                            # id needs to be the parent_recid
                            self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                "end_date": end_date, 
                                                                "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        if unique:
                            num_downloads += response["downloads"]["unique_downloads"]
                        else:
                            num_downloads += response["downloads"]["downloads"]
            
                    date_key = month_str + "-" + str(start_year)
                    avg_downloads[date_key] = num_downloads / total_deposits
                    
                    return avg_downloads

                else:        
                    num_days = calendar.monthrange(year_num, month_num)[1]
                    last_mo_day = datetime.date(year_num, month_num, num_days)
                    for id in self.deposits:
                        if version.lower() == "current":
                            self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                                    "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                            "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                            "recid": id}}})
                        else:
                            # id needs to be the parent_recid
                            self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                        "params": {"start_date": date_holder.strftime('%Y-%m-%d'), 
                                                                    "end_date": last_mo_day.strftime('%Y-%m-%d'), 
                                                                    "parent_recid": id}}})
                        response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                        if unique:
                            num_downloads += response["downloads"]["unique_downloads"]
                        else:
                            num_downloads += response["downloads"]["downloads"]
                
                    date_key = month_str + "-" + str(start_year)
                    avg_downloads[date_key] = num_downloads / total_deposits
                    date_holder = last_mo_day + datetime.timedelta(days=1)

        elif freq.lower() == "weekly" and start_date != None and end_date != None:
            avg_downloads = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)
            day_of_week = start_datetime.weekday()
            if day_of_week == 6:
                init_delta = datetime.timedelta(days=6)
            else:
                init_delta = datetime.timedelta(days=5-day_of_week)
            start_week = start_datetime
            end_week = start_datetime + init_delta
            delta = datetime.timedelta(days=6)

            while (start_week <= end_datetime):
                num_downloads = 0
                for id in self.deposits:
                    if version.lower() == "current":
                        self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                            "end_date": (end_datetime.strftime("%Y-%m-%d") 
                                                                            if end_week > end_datetime else end_week.strftime("%Y-%m-%d")), 
                                                            "recid": id}}})
                    else:
                        self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": start_week.strftime("%Y-%m-%d"), 
                                                            "end_date": (end_datetime.strftime("%Y-%m-%d") 
                                                                            if end_week > end_datetime else end_week.strftime("%Y-%m-%d")), 
                                                            "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        num_downloads += response["downloads"]["unique_downloads"]
                    else:
                        num_downloads += response["downloads"]["downloads"]

                date_key = "Week of " + start_week.strftime("%Y-%m-%d") + " - " + \
                            (end_datetime.strftime("%Y-%m-%d") if end_week > end_datetime else end_week.strftime("%Y-%m-%d"))
                avg_downloads[date_key] = num_downloads / total_deposits
                start_week = end_week + datetime.timedelta(days=1)
                end_week = start_week + delta
            
            return avg_downloads
        
        elif freq.lower() == "daily" and start_date != None and end_date != None:
            avg_downloads = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = datetime.date(start_year, start_month, start_day)
            end_datetime = datetime.date(end_year, end_month, end_day)
            delta = datetime.timedelta(days=1)
                    
            while (start_datetime <= end_datetime):
                num_downloads = 0
                for id in self.deposits:
                    if version.lower() == "current":
                        self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                    "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "recid": id}}})
                    else:
                        self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                    "params": {"start_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "end_date": start_datetime.strftime("%Y-%m-%d"), 
                                                                "parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        num_downloads += response["downloads"]["unique_downloads"]
                    else:
                        num_downloads += response["downloads"]["downloads"]

                avg_downloads[start_datetime.strftime("%Y-%m-%d")] = num_downloads / total_deposits
                start_datetime += delta

            return avg_downloads
        

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
