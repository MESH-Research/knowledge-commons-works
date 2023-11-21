import requests

# create class for managing stats queried from Invenio API response

class APIResponse():
    # constructor: an APIResponse object keeps track of headers for the API request, the JSON response from
    # the records endpoint, and a dictionary mapping id->deposit info
    def __init__(self, bearer_token):
        self.headers = {'Authorization': 'Bearer ' + bearer_token}
        self.records_json = None
        self.deposits = {}

    # function that returns JSON object from a GET request to records endpoint
    # also creates dictionary mapping deposit ID to dictionary of deposit info (from records endpoint)
    def get_records(self):
        get_records_url = 'https://invenio-dev.hcommons-staging.org/api/records'
        # send GET request to records endpoint, save JSON response
        self.records_json = requests.get(get_records_url, headers=self.headers, verify=False).json()
        # create the dictionary
        for item in self.records_json['hits']['hits']:
            id = item['id']
            self.deposits[id] = item

    # function that returns the total number of deposits
    def total_deposits(self):
        if self.records_json == None:
            self.get_records()
        return self.records_json['hits']['total']
    
    # function that returns the total num of views of a deposit
    def total_views(self, id):
        if self.records_json == None:
            self.get_records()
        if id == 'all':
            views_dict = {}
            for key in self.deposits:
                views_dict[key] = self.deposits[key]['stats']['this_version']['views']
            return views_dict
        else:
            deposit = self.deposits[id]
            return deposit['stats']['this_version']['views']

    # function that returns the average num of views across all deposits
    def avg_views(self):
        if self.records_json == None:
            self.get_records()

        total_views = 0
        for key in self.deposits:
            no_views = self.deposits[key]['stats']['this_version']['views']
            total_views += no_views
        
        total_deposits = self.records_json['hits']['total']
        return total_views / total_deposits
    
    # function that returns the total num of downloads of a deposit
    def total_downloads(self, id):
        if self.records_json == None:
            self.get_records()
        if id == 'all':
            downloads_dict = {}
            for key in self.deposits:
                downloads_dict[key] = self.deposits[key]['stats']['this_version']['downloads']
            return downloads_dict
        else:
            deposit = self.deposits[id]
            return deposit['stats']['this_version']['downloads']

    # function that returns the average num of downloads across all deposits
    def avg_downloads(self):
        if self.records_json == None:
            self.get_records()

        total_downloads = 0
        for key in self.deposits:
            no_downloads = self.deposits[key]['stats']['this_version']['downloads']
            total_downloads += no_downloads
        
        total_deposits = self.records_json['hits']['total']
        return total_downloads / total_deposits
        
        