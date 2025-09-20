
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

class DriveAuthenticator:
    def __init__(self, credentials_file):
        """
        Initializes the authenticator with a specific file to save/load credentials.
        :param credentials_file: The path to the file for storing credentials (e.g., 'credentials_source.json')
        """
        self.credentials_file = credentials_file

    def authenticate(self):
        """
        Performs the authentication flow and returns an authenticated GoogleDrive instance.
        """
        gauth = GoogleAuth()

        if os.path.exists('client_secrets.json'):
            gauth.settings['client_config_file'] = 'client_secrets.json'
        else:
            raise FileNotFoundError("'client_secrets.json' not found. Please run auth_helper.py first.")


        gauth.LoadCredentialsFile(self.credentials_file)

        if gauth.credentials is None:

            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:

            gauth.Refresh()
        else:

            gauth.Authorize()

        gauth.SaveCredentialsFile(self.credentials_file)

        return GoogleDrive(gauth)
