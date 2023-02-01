# File used to connect with the API
from requests import post, get
import json
from urllib.parse import urlencode

import base64
from dotenv import load_dotenv
import os
import datetime 

# Accessing Information from your .env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

####################
# Creating a Class #
####################

class SpotifyAPI(object):

    access_token = None
    access_token_expires = None
    access_token_expired = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_creds(self):
        """
            Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        # Ensuring client_id and client_secrets have values
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client secret")
        # Auth String BEFORE encoding
        auth_string = client_id + ":" + client_secret
        # This is currently a string, but to encode the string using base64, we need to convert it into BYTES
        # Convert the String Into Bytes
        auth_bytes = auth_string.encode()
        # Encode String in Base64
        encoded_auth = base64.b64encode(auth_bytes)

        return encoded_auth.decode()

    def get_token_header(self):
        client_creds_b64 = self.get_client_creds()

        return {
            "Authorization": "Basic " + client_creds_b64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()

        # INSERT Performing the Request
        response = post(token_url, data=token_data, headers=token_headers)

        # INSERT Check if Request is Valid
        valid_request = response.status_code in range(200, 299)

        if not valid_request:
            raise Exception("Could not authenticate Client")

        # INSERT Pulling Necessary Data from the Response
        now = datetime.datetime.now()
        data = response.json()
        access_token = data['access_token']
        self.access_token = access_token
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires
        self.access_token_expired = expires < now
        
        return True

    def get_access_token(self):
        auth_done = self.perform_auth()
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()

        headers = {
            "Authorization" : "Bearer " + access_token,
            "Content-Type": "application/json" 
        }

        return headers

    def search(self, query=None, search_type='track'):
        if query == None:
            raise Exception("A query is required")
        
        if isinstance(query, dict):
            #turns a dictionary into a list
            query_list = [ k + ":" + v for k,v in query.items()]
            query = " ".join(query_list)

        query_params = urlencode({"q": query, "type": search_type.lower(), "limit": "1"})

        headers = self.get_resource_header()

        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = endpoint + "?" + query_params

        response = get(lookup_url, headers=headers)
        
        if response.status_code not in range(200,299):
            return {}
        
        return response.json()
    
    def get_audio_analysis(self, _id):
        if _id == None:
            raise Exception("An id is required")

        headers = self.get_resource_header()
        
        endpoint = "https://api.spotify.com/v1/audio-features/"
        lookup_url = endpoint + str(_id)

        response = get(lookup_url, headers=headers)
        if response.status_code not in range(200,299):
            return {}
        
        return response.json()
