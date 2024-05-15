import requests
import numpy as np
import json
import calendar
import itertools
import urllib.parse
import datetime as dt
from datetime import datetime
from collections import OrderedDict

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
        self.deposits = {}
        self.records_url = 'https://invenio-dev.hcommons-staging.org/api/records'
        self.stats_url = 'https://invenio-dev.hcommons-staging.org/api/stats'


    # function that returns JSON string from a GET request to records endpoint
    # also creates dictionary mapping deposit ID to dictionary of deposit info (from records endpoint)
    def get_records(self, version):
        # .json() turns the JSON string into a python dictionary
        self.records = requests.get(self.records_url, headers=self.headers).json()
        # create the dictionary
        for item in self.records['hits']['hits']:
            if version == 'current':
                id = item['id']
            else:
                id = item['parent']['id']
            self.deposits[id] = item
            

    # function that returns the number of deposits, either over time or total
    def num_deposits(self, freq=None, latest=False):
        if self.records == None:
            self.get_records('current')

        # might need to do time sorting for dictionaries returned?
        if freq == None:
            no_deposits = self.records['hits']['total']
            return {'title': 'Total number of deposits currently', 'stat': no_deposits}

        else:
            if freq.lower() == 'monthly':
                """
                time_dict = {}
                for key in self.deposits:
                    remove_time = self.deposits[key]['created'].split('T')
                    y_m_d = remove_time[0].split('-')
                    month_year = y_m_d[1] + '-' + y_m_d[0] 
                    time_dict[month_year] = time_dict.get(month_year, 0) + 1
                """
                if latest:
                    current_date = datetime.now()
                    current_month = str(current_date.month) if int(current_date.month) > 9 else '0' + str(current_date.month)
                    current_year = str(current_date.year)
                    current_month_str = 'Month of ' + current_month + '-' + current_year
                    start_mo = current_year + '-' + current_month + '-01'
                    num_days = calendar.monthrange(int(current_year), int(current_month))[1]
                    end_mo = current_year + '-' + current_month + '-' + str(num_days)
                    encoded_query = urllib.parse.quote(f"[{start_mo} TO {end_mo}]")
                    url = f"{self.records_url}?q=created:{encoded_query}"
                    month_deposits_response = requests.get(url, headers=self.headers).json()
                    no_deposits = month_deposits_response['hits']['total']
                    return {'title': current_month_str, 'stat': no_deposits}
            
            # weekly: isocalendar() from datetime.time
            elif freq.lower() == 'weekly':
                """
                time_dict = {}
                for key in self.deposits:
                    remove_time = self.deposits[key]['created'].split('T')
                    y_m_d = remove_time[0].split('-')
                    date_tuple = dt.date(int(y_m_d[0]), int(y_m_d[1]), int(y_m_d[2]))
                    year = date_tuple.isocalendar()[0]
                    week = date_tuple.isocalendar()[1]
                    week_str = 'Week ' + str(week) + ', ' + str(year)
                    time_dict[week_str] = time_dict.get(week_str, 0) + 1
                """
                if latest:
                    current_date = datetime.now()
                    # current_week = current_date.isocalendar()[1]
                    current_year = str(current_date.year)
                    # current_week_str = 'Week ' + str(current_week) + ', ' + current_year
                    start_week = current_date - dt.timedelta(days=current_date.weekday())
                    end_week = start_week + dt.timedelta(days=6)
                    start_week = start_week.strftime('%Y-%m-%d')
                    end_week = end_week.strftime('%Y-%m-%d')
                    encoded_query = urllib.parse.quote(f"[{start_week} TO {end_week}]")
                    url = f"{self.records_url}?q=created:{encoded_query}"
                    week_deposits_response = requests.get(url, headers=self.headers).json()
                    no_deposits = week_deposits_response['hits']['total']
                    current_week_str = 'Week of ' + start_week + ' - ' + end_week
                    return {'title': current_week_str, 'stat': no_deposits}
            
            elif freq.lower() == 'daily':
                """
                time_dict = {}
                for key in self.deposits:
                    remove_time = self.deposits[key]['created'].split('T')
                    y_m_d = remove_time[0]
                    time_dict[y_m_d] = time_dict.get(y_m_d, 0) + 1
                """
                if latest:
                    current_date = datetime.now()
                    current_date_str = str(current_date.year) + '-' \
                                        + (str(current_date.month) if int(current_date.month) > 9 else '0' + str(current_date.month)) \
                                        + '-' + (str(current_date.day) if int(current_date.day) > 9 else '0' + str(current_date.day))
                    url = self.records_url + '?q=created:' + current_date_str
                    day_deposits_response = requests.get(url, headers=self.headers).json()
                    no_deposits = day_deposits_response['hits']['total']
                    return {'title': current_date_str, 'stat': no_deposits}
        
        # return time_dict
        
    
    # function that returns the total num of views of a deposit
    def num_views(self, id, version=None, start_date=None, end_date=None, freq=None, unique=None):
        if id == 'all':
            self.get_records(version)
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
                start_datetime = dt.date(start_year, start_month, start_day)
                end_datetime = dt.date(end_year, end_month, end_day)

                if freq.lower() == "monthly":
                    month_num = start_datetime.month
                    if month_num < 10:
                        month_str = "0" + str(month_num)
                    else:
                        month_str = str(month_num)
                    num_days = calendar.monthrange(start_year, month_num)[1]
                    last_mo_day = dt.date(start_year, month_num, num_days)
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
                    date_holder = last_mo_day + dt.timedelta(days=1)

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
                            last_mo_day = dt.date(year_num, month_num, num_days)
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
                        date_holder = last_mo_day + dt.timedelta(days=1)
                
                elif freq.lower() == "weekly":
                    day_of_week = start_datetime.weekday()
                    if day_of_week == 6:
                        init_delta = dt.timedelta(days=6)
                    else:
                        init_delta = dt.timedelta(days=5-day_of_week)
                    start_week = start_datetime
                    end_week = start_datetime + init_delta
                    delta = dt.timedelta(days=6)

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
                        
                        start_week = end_week + dt.timedelta(days=1)
                        end_week = start_week + delta
                    
                    return views_over_time
                
                else:
                    delta = dt.timedelta(days=1)
                    
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
    def avg_views(self, version, freq, start_date, end_date, latest, unique):
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
                elif version.lower() == "all" and unique == True:
                    no_views = self.deposits[key]['stats']['all_versions']['unique_views']
                    total_views += no_views
                else:
                    no_views = self.deposits[key]['stats']['all_versions']['views']
                    total_views += no_views
            return {'title': 'Average no. of views per deposit currently', 'stat': total_views / total_deposits}
        
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
                elif version.lower() == "all" and unique == True:
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

            return round(total_views / total_deposits, 2)
        
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
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)

            month_num = start_datetime.month
            if month_num < 10:
                month_str = "0" + str(month_num)
            else:
                month_str = str(month_num)
            num_days = calendar.monthrange(start_year, month_num)[1]
            last_mo_day = dt.date(start_year, month_num, num_days)

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
            avg_views[date_key] = round(num_views / total_deposits, 2)

            date_holder = last_mo_day + dt.timedelta(days=1)

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
                    avg_views[date_key] = round(num_views / total_deposits, 2)
                    
                    return avg_views

                else:        
                    num_days = calendar.monthrange(year_num, month_num)[1]
                    last_mo_day = dt.date(year_num, month_num, num_days)
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
                    avg_views[date_key] = round(num_views / total_deposits, 2)
                    date_holder = last_mo_day + dt.timedelta(days=1)

        elif freq.lower() == "monthly" and latest:
            current_date = datetime.now()
            first_date = f'{current_date.year}-{current_date.month}-01'

            num_views = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"views": {"stat": "record-view", 
                                                        "params": {"start_date": first_date, 
                                                                    "end_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                "params": {"start_date": first_date, 
                                                            "end_date": current_date.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_views += response["views"]["unique_views"]
                else:
                    num_views += response["views"]["views"]
            
            avg_views_latest_mo = round(num_views / total_deposits, 2)
            month_str = f'{current_date.month}-{current_date.year}'

            return {'time': month_str, 'stat': avg_views_latest_mo}
        
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
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)
            day_of_week = start_datetime.weekday()
            if day_of_week == 6:
                init_delta = dt.timedelta(days=6)
            else:
                init_delta = dt.timedelta(days=5-day_of_week)
            start_week = start_datetime
            end_week = start_datetime + init_delta
            delta = dt.timedelta(days=6)

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
                avg_views[date_key] = round(num_views / total_deposits, 2)
                start_week = end_week + dt.timedelta(days=1)
                end_week = start_week + delta
            
            return avg_views
        
        elif freq.lower() == "weekly" and latest:
            current_date = datetime.now()
            first_date = current_date - dt.timedelta(days=current_date.weekday()+1)

            num_views = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"views": {"stat": "record-view", 
                                                        "params": {"start_date": first_date.strftime('%Y-%m-%d'), 
                                                                    "end_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                "params": {"start_date": first_date.strftime('%Y-%m-%d'), 
                                                            "end_date": current_date.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_views += response["views"]["unique_views"]
                else:
                    num_views += response["views"]["views"]
            
            avg_views_latest_week = round(num_views / total_deposits, 2)
            week_str = first_date.strftime('%Y-%m-%d') + ' - ' + current_date.strftime('%Y-%m-%d')

            return {'time': week_str, 'stat': avg_views_latest_week}

        
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
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)
            delta = dt.timedelta(days=1)
                    
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

                avg_views[start_datetime.strftime("%Y-%m-%d")] = round(num_views / total_deposits, 2)
                start_datetime += delta

            return avg_views

        elif freq.lower() == "daily" and latest:
            current_date = datetime.now()

            num_views = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"views": {"stat": "record-view", 
                                                        "params": {"start_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "end_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"views": {"stat": "record-view-all-versions", 
                                                "params": {"start_date": current_date.strftime('%Y-%m-%d'), 
                                                            "end_date": current_date.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_views += response["views"]["unique_views"]
                else:
                    num_views += response["views"]["views"]
            
            avg_views_today = round(num_views / total_deposits, 2)
            today_str = current_date.strftime('%Y-%m-%d')

            return {'time': today_str, 'stat': avg_views_today}

    
    # function that returns the total num of downloads of a deposit
    def num_downloads(self, id, version=None, start_date=None, end_date=None, freq=None, unique=None):
        if id == 'all':
            self.get_records(version)
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
            if freq == None:
                if version.lower() == "current":
                    self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                        "params": {"recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        num_downloads = response["downloads"]["unique_downloads"]
                    else:
                        num_downloads = response["downloads"]["downloads"]
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"downloads-all-versions": {"stat": "record-download-all-versions", 
                                                "params": {"parent_recid": id}}})
                    response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                    if unique:
                        num_downloads = response["downloads-all-versions"]["unique_downloads"]
                    else:
                        num_downloads = response["downloads-all-versions"]["downloads"]
                return num_downloads

            downloads_over_time = {}
            start_y_m_d = start_date.split("-")
            start_year = int(start_y_m_d[0])
            start_month = int(start_y_m_d[1].lstrip('0'))
            start_day = int(start_y_m_d[2])
            end_y_m_d = end_date.split("-")
            end_year = int(end_y_m_d[0])
            end_month = int(end_y_m_d[1].lstrip('0'))
            end_day = int(end_y_m_d[2])
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)

            if freq.lower() == "monthly":
                month_num = start_datetime.month
                if month_num < 10:
                    month_str = "0" + str(month_num)
                else:
                    month_str = str(month_num)
                num_days = calendar.monthrange(start_year, month_num)[1]
                last_mo_day = dt.date(start_year, month_num, num_days)
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
                date_holder = last_mo_day + dt.timedelta(days=1)

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
                        last_mo_day = dt.date(year_num, month_num, num_days)
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
                    date_holder = last_mo_day + dt.timedelta(days=1)
            
            elif freq.lower() == "weekly":
                day_of_week = start_datetime.weekday()
                if day_of_week == 6:
                    init_delta = dt.timedelta(days=6)
                else:
                    init_delta = dt.timedelta(days=5-day_of_week)
                start_week = start_datetime
                end_week = start_datetime + init_delta
                delta = dt.timedelta(days=6)

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

                    start_week = end_week + dt.timedelta(days=1)
                    end_week = start_week + delta
                
                return downloads_over_time
            
            else:
                delta = dt.timedelta(days=1)
                
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
    def avg_downloads(self, version, freq, start_date, end_date, latest, unique):
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
                elif version.lower() == "all" and unique == True:
                    total_downloads += self.deposits[key]['stats']['all_versions']['unique_downloads']
                else:
                    total_downloads += self.deposits[key]['stats']['all_versions']['downloads']
            return {'title': 'Average no. of downloads per deposit currently', 'stat': total_downloads / total_deposits}
        
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
                elif version.lower() == "all" and unique == True:
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

            return round(total_downloads / total_deposits, 2)
        
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
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)

            month_num = start_datetime.month
            if month_num < 10:
                month_str = "0" + str(month_num)
            else:
                month_str = str(month_num)
            num_days = calendar.monthrange(start_year, month_num)[1]
            last_mo_day = dt.date(start_year, month_num, num_days)

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
            avg_downloads[date_key] = round(num_downloads / total_deposits, 2)

            date_holder = last_mo_day + dt.timedelta(days=1)

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
                    avg_downloads[date_key] = round(num_downloads / total_deposits, 2)
                    
                    return avg_downloads

                else:        
                    num_days = calendar.monthrange(year_num, month_num)[1]
                    last_mo_day = dt.date(year_num, month_num, num_days)
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
                    avg_downloads[date_key] = round(num_downloads / total_deposits, 2)
                    date_holder = last_mo_day + dt.timedelta(days=1)

        elif freq.lower() == "monthly" and latest:
            current_date = datetime.now()
            first_date = f'{current_date.year}-{current_date.month}-01'

            num_downloads = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                        "params": {"start_date": first_date, 
                                                                    "end_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": first_date, 
                                                            "end_date": current_date.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_downloads += response["downloads"]["unique_downloads"]
                else:
                    num_downloads += response["downloads"]["downloads"]
            
            avg_downloads_latest_mo = round(num_downloads / total_deposits, 2)
            month_str = f'{current_date.month}-{current_date.year}'

            return {'time': month_str, 'stat': avg_downloads_latest_mo}
        
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
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)
            day_of_week = start_datetime.weekday()
            if day_of_week == 6:
                init_delta = dt.timedelta(days=6)
            else:
                init_delta = dt.timedelta(days=5-day_of_week)
            start_week = start_datetime
            end_week = start_datetime + init_delta
            delta = dt.timedelta(days=6)

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
                avg_downloads[date_key] = round(num_downloads / total_deposits, 2)
                start_week = end_week + dt.timedelta(days=1)
                end_week = start_week + delta
            
            return avg_downloads
        
        elif freq.lower() == "weekly" and latest:
            current_date = datetime.now()
            first_date = current_date - dt.timedelta(days=current_date.weekday()+1)

            num_downloads = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                        "params": {"start_date": first_date.strftime('%Y-%m-%d'), 
                                                                    "end_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": first_date.strftime('%Y-%m-%d'), 
                                                            "end_date": current_date.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_downloads += response["downloads"]["unique_downloads"]
                else:
                    num_downloads += response["downloads"]["downloads"]
            
            avg_downloads_latest_week = round(num_downloads / total_deposits, 2)
            week_str = first_date.strftime('%Y-%m-%d') + ' - ' + current_date.strftime('%Y-%m-%d')

            return {'time': week_str, 'stat': avg_downloads_latest_week}
        
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
            start_datetime = dt.date(start_year, start_month, start_day)
            end_datetime = dt.date(end_year, end_month, end_day)
            delta = dt.timedelta(days=1)
                    
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

                avg_downloads[start_datetime.strftime("%Y-%m-%d")] = round(num_downloads / total_deposits, 2)
                start_datetime += delta

            return avg_downloads

        elif freq.lower() == "daily" and latest:
            current_date = datetime.now()

            num_downloads = 0
            for id in self.deposits:
                if version.lower() == "current":
                    self.payload = json.dumps({"downloads": {"stat": "record-download", 
                                                        "params": {"start_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "end_date": current_date.strftime('%Y-%m-%d'), 
                                                                    "recid": id}}})
                else:
                    # id needs to be the parent_recid
                    self.payload = json.dumps({"downloads": {"stat": "record-download-all-versions", 
                                                "params": {"start_date": current_date.strftime('%Y-%m-%d'), 
                                                            "end_date": current_date.strftime('%Y-%m-%d'), 
                                                            "parent_recid": id}}})
                response = requests.post(self.stats_url, headers=self.headers, data=self.payload, verify=False).json()
                if unique:
                    num_downloads += response["downloads"]["unique_downloads"]
                else:
                    num_downloads += response["downloads"]["downloads"]
            
            avg_downloads_today = round(num_downloads / total_deposits, 2)
            today_str = current_date.strftime('%Y-%m-%d')

            return {'time': today_str, 'stat': avg_downloads_today}
        
    # determine the top 100 deposits by no. of views, and determine stats of those deposits
    def top_views(self, num):
        """
        self.get_records('current')
        views = self.num_views('all', 'current')
        keys = list(views.keys())
        values = list(views.values())
        sorted_indices = np.argsort(values)
        sorted_dict = OrderedDict()
        sorted_dict = {keys[i]: values[i] for i in sorted_indices}
        for id in sorted_dict:
            sorted_dict[id] = self.deposits[id]
        top_100_views_dict = dict(itertools.islice(sorted_dict.items(), num))
        """
        url = self.records_url + '?sort=mostviewed&size=' + str(num)
        top_views_response = requests.get(url, headers=self.headers).json()
        top_views_dict = OrderedDict()
        for deposit in top_views_response['hits']['hits']:
            id = deposit['id']
            no_views = deposit['stats']['this_version']['views']
            no_unique_views = deposit['stats']['this_version']['unique_views']
            no_downloads = deposit['stats']['this_version']['downloads']
            no_unique_downloads = deposit['stats']['this_version']['unique_downloads']
            top_views_dict[id] = [no_views, no_unique_views, no_downloads, no_unique_downloads]

        return top_views_dict
    
    # determine the top 100 deposits by no. of downloads, and determine stats of those deposits
    def top_downloads(self, num):
        """
        downloads = self.num_downloads('all', 'current')
        keys = list(downloads.keys())
        values = list(downloads.values())
        sorted_indices = np.argsort(values)
        sorted_dict = OrderedDict()
        sorted_dict = {keys[i]: values[i] for i in sorted_indices}
        for id in sorted_dict:
            sorted_dict[id] = self.deposits[id]
        top_100_downloads_dict = dict(itertools.islice(sorted_dict.items(), num))
        """
        url = self.records_url + '?sort=mostdownloaded&size=' + str(num)
        top_downloads_response = requests.get(url, headers=self.headers).json()
        top_downloads_dict = OrderedDict()
        for deposit in top_downloads_response['hits']['hits']:
            id = deposit['id']
            no_views = deposit['stats']['this_version']['views']
            no_unique_views = deposit['stats']['this_version']['unique_views']
            no_downloads = deposit['stats']['this_version']['downloads']
            no_unique_downloads = deposit['stats']['this_version']['unique_downloads']
            top_downloads_dict[id] = [no_views, no_unique_views, no_downloads, no_unique_downloads]

        return top_downloads_dict
