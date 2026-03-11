import requests
import json

def get_tokens(client_id: str, client_secret: str, access_level: str = None, redirect_uri = "http://localhost"):
        """ 
        Helper function - to get OAuth2 tokens
        access_level = file/readonly. If not specified - full access
        """
        
        scope = "https://www.googleapis.com/auth/drive"
        if access_level in ("file", "readonly"):
            scope += "." + access_level
        
        # STEP1
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        print(f"Go to this URL in your browser:\n\n{auth_url}\n")
        
        #STEP2
        auth_code = input("Enter the 'code' parameter from the URL you were redirected to: ")

        #STEP3
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        response = requests.post(token_url, data = data)
        tokens = response.json()

        if tokens.get('access_token'):
            print("Access & Refresh tokens retrieved")
        return tokens

class google_drive:
    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token

    def refresh_access_token(self):
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        response = requests.post(url, data = data)
        self.access_token = response.json()['access_token']

    def list_items(self, page_size: int = 1000):
        url = "https://www.googleapis.com/drive/v3/files"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "pageSize": page_size, 
            "fields": "nextPageToken, files(id, name, parents, mimeType)"
        }
        items = []
        next_page_token = None
        while True:
            if next_page_token:
                params['pageToken'] = next_page_token
            res = requests.get(url, headers = headers, params = params).json()
            tmp_items = res.get("files", [])
            items.extend(tmp_items)
            next_page_token = res.get("nextPageToken")
            print(len(tmp_items))
            if not next_page_token:
                break
        print(f"Listed {len(items)} items.")
        return items

    def get_item_by_name(self, item_name):
        url = "https://www.googleapis.com/drive/v3/files"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": f"name = '{item_name}' and trashed = false",
            "fields": "files(id, name, mimeType, parents)"
        }
        res = requests.get(url, headers = headers, params = params)
        return res.json()["files"]
    
    def get_item_by_id(self, item_id):
        url = f"https://www.googleapis.com/drive/v3/files/{item_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"fields": "name, mimeType, parents"}
        res = requests.get(url, headers = headers, params = params)
        return res.json()
    
    def delete_item(self, item_id):
        url = f"https://www.googleapis.com/drive/v3/files/{item_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(url, headers = headers)
        if response.status_code == 204:
            print(f"Item {item_id} permanently deleted.")
        else:
            print(f"Error deleting item: {response.text}")
    
    def upload_file(self, source_file_name: str, destination_file_name: str = None, folder_id = None):
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        file_metadata = {}
        if destination_file_name:
            file_metadata["name"] = destination_file_name
        else:
            file_metadata["name"] = source_file_name.split("/")[-1]
        if folder_id:
            file_metadata["parents"] = [folder_id]
        
        files = {
            "data": ("metadata", json.dumps(file_metadata), "application/json; charset=UTF-8"),
            "file": open(source_file_name, "rb")
        }

        response = requests.post(url, headers = headers, files = files)
        if response.status_code == 200:
            print(f"Upload Successful! File ID: {response.json().get('id')}")
            return response.json()
        else:
            print(f"Upload Failed: {response.text}")
            return None

# ---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Google Drive simple test")
    
    with open("gd_creds.json") as f:
        credentials = json.load(f)

    # tokens = get_tokens(client_id = credentials['client_id'], client_secret = credentials['client_secret'])
    # credentials["access_token"] = tokens["access_token"]
    # credentials["refresh_token"] = tokens["refresh_token"]
    # with open("gd_creds.json", "w") as f:
    #     json.dump(credentials, f)

    gd = google_drive(
        client_id = credentials['client_id'], 
        client_secret = credentials['client_secret'],
        access_token = credentials['access_token'],
        refresh_token = credentials['refresh_token']
    )

    gd.refresh_access_token()

    items = gd.list_items()