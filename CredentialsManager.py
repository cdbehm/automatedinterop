import json


class CredentialsManager(object):
    user = ""
    password = ""
    config_path = 'C:\shs_assets_config.json'
    config = None
    def __init__(self , dealer_id):
        with open(self.config_path) as config_file:
            self.config = json.load(config_file)
        if not dealer_id in self.config['valid_dealers']:
            print('Invalid dealer id')
        else:
            self.user = self.config['credentials'][str(dealer_id)]['user']
            self.password = self.config['credentials'][str(dealer_id)]['password']