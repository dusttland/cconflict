from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Your client credentials
client_id = "Can't tell you this."
client_secret = "Can't tell you this either."

# Create a session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Get token for the session
token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                          client_secret=client_secret)

# All requests using this session will have an access token automatically added
data = {
    "bbox": [13, 45, 14, 46],
    "datetime": "2019-12-10T00:00:00Z/2019-12-10T23:59:59Z",
    "collections": ["sentinel-1-grd"],
    "limit": 5,
}

url = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"
response = oauth.post(url, json=data)

print(response.status_code)
print(response.content)
