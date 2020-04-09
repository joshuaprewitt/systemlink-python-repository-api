"""
Class for uploading packages to the Package Repository's package pool, and
adding them to a feed. Can be run from the command line.
"""
import argparse
import sys
import time
from os.path import basename

import requests
from requests import Response
from requests.auth import HTTPBasicAuth
import urllib3

class RepoError(Exception):
    """Base class for exceptions in this module"""
    pass

class Uploader:
    """Class for uploading packages to the Package Repository's package pool, and adding
    them to a feed. Can be run from the command line.
    Note that, in the Package Repository, adding a brand new package to a feed is a two step
    process. New packages must first be added to the package pool. After a package is in the
    package pool, it can then be added to a feed.
    """

    # Replace this with your server's hostname and port
    DEFAULT_SERVER_URL = 'https://localhost:9091/'

    # Authentication constants (replace these with the username and password used for
    # authenticating to SystemLink)
    DEFAULT_USERNAME = 'admin'
    DEFAULT_PASSWORD = 'test'

    UPLOAD_PACKAGE = 'nirepo/v1/upload-packages?shouldOverwrite={should_overwrite}'
    GET_JOB = 'nirepo/v1/jobs/{job_id}'
    ADD_PACKAGE_REFERENCE = 'nirepo/v1/feeds/{feed_id}/add-package-references'
    CREATE_FEED = 'nirepo/v1/feeds'
    GET_FEEDS = 'nirepo/v1/feeds'

    JOB_WAIT_SLEEP_TIME_SECONDS = 1

    def __init__(self, systemlink_server_url=None, username=None, password=None):
        self.set_server_parameters(systemlink_server_url=systemlink_server_url,
                                   username=username, password=password)

    def set_server_parameters(self, systemlink_server_url=None, username=None, password=None):
        """Function for initializing server url, username, and password parameters."""
        if systemlink_server_url is None:
            self.systemlink_server_url = self.DEFAULT_SERVER_URL
        else:
            self.systemlink_server_url = systemlink_server_url

        if self.systemlink_server_url[-1:] != '/':
            self.systemlink_server_url = self.systemlink_server_url + '/'

        if username is None:
            self.username = self.DEFAULT_USERNAME
        else:
            self.username = username

        if password is None:
            self.password = self.DEFAULT_PASSWORD
        else:
            self.password = password

        self.upload_package_url = self.systemlink_server_url + self.UPLOAD_PACKAGE
        self.get_job_url = self.systemlink_server_url + self.GET_JOB
        self.add_package_url = self.systemlink_server_url + self.ADD_PACKAGE_REFERENCE
        self.create_feed_url = self.systemlink_server_url + self.CREATE_FEED
        self.get_feeds_url = self.systemlink_server_url + self.GET_FEEDS
        self.auth = HTTPBasicAuth(self.username, self.password)

    def run(self):
        """Function for uploading a package to a feed when running from the command line."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--filename', type=str,
                            help='the path to the package to be uploaded',
                            required=True)
        parser.add_argument('--feedId', type=str,
                            help='the ID of the feed to add the uploaded package to',
                            required=True)
        parser.add_argument('--serverUrl', type=str,
                            help='the systemlink server url, e.g, https://localhost:9091',
                            required=False)
        parser.add_argument('--username', type=str,
                            help='the username to authenticate to the systemlink server with',
                            required=False)
        parser.add_argument('--password', type=str,
                            help='the password to authenticate to the systemlink server with',
                            required=False)
        args = parser.parse_args()
        self.set_server_parameters(systemlink_server_url=args.serverUrl, username=args.username,
                                   password=args.password)
        try:
            print('Uploading the package to the package pool...')
            package_id = self.upload_package(filename=args.filename)
            print('Adding the package to the feed...')
            self.add_package_reference(package_id=package_id, feed_id=args.feedId)
        except RepoError as error:
            print(error)
            sys.exit(1)
        sys.exit(0)
    
    def get_feeds(self):
        response = requests.get(url=self.get_feeds_url, auth=(self.username, self.password), verify=False)
        return response
    
    def create_feed(self, feed_name, name, description='', platform='windows', workspace=None):
        feed_info = {
            "feedName": feed_name,
            "name": name,
            "description": description,
            "platform": platform,
            "workspace": workspace
        }
        response = requests.post(url=self.create_feed_url, json=feed_info, auth=(self.username, self.password), verify=False)
        if response.status_code >= 300:
            print("Error: Request to create a feed returned status code {status_code} "
                  "with message {message}"
                  .format(status_code=response.status_code, message=response.json()))
        else:
            try:
                procesed_job = self.process_job_result(job_id=response.json()['jobId'])
                print(procesed_job)
            except RepoError:
                pass

    # Function for clients wishing to call the class programmatically
    def upload_and_add(self, filename: str, feed_id: str):
        """Function to add a package to a feed."""
        try:
            package_id = self.upload_package(filename=filename)
            self.add_package_reference(package_id=package_id, feed_id=feed_id)
        except RepoError as error:
            print(error)

    def add_package_reference(self, package_id: str, feed_id: str):
        """Adds a package which already exists in the Package Repository's package pool
        to a feed."""
        url = self.add_package_url.format(feed_id=feed_id)
        json = {
            'packageReferences': [package_id]
        }
        response = requests.post(
            url=url,
            json=json,
            auth=self.auth,
            verify=False
        )
        if response.status_code != 202:
            print("Error: Request to add package reference returned status code {status_code} "
                  "with message {message}"
                  .format(status_code=response.status_code, message=response.json()))
        self.process_job_result(job_id=response.json()['jobId'])

    def upload_package(self, filename: str) -> str:
        """Uploads a package to the Package Repository's package pool."""
        url = self.upload_package_url.format(should_overwrite=0)
        # Note: to upload packages hosted on the network, instead of a file present on disk,
        # replace open('filename') with a call to urllib.urlopen(uri). Note that you might
        # need to pass a context object which disables SSL validation. See the commented out
        # function at the end of this file for a way to do that.
        files = {
            'file':
            (
                basename(filename), open(filename, 'rb'), 'multipart/form-data'
            )
        }
        response = requests.post(
            url=url,
            files=files,
            auth=self.auth,
            verify=False
        )

        if response.status_code != 202:
            raise RepoError("Error: Request to upload package returned status code {status_code}"
                            "with message {message}"
                            .format(status_code=response.status_code, message=response.text))

        package = self.process_job_result(job_id=response.json()['jobIds'][0])
        if 'package' not in package:
            raise RepoError("Error: Response missing 'package' object")

        return package['package']['id']

    def process_job_result(self, job_id: str) -> str:
        """Poll a job until it completes. Returns the resource created or modified
        by the job on success, or the job object on failure."""
        url = self.get_job_url.format(job_id=job_id)
        response = requests.get(
            url=url,
            auth=self.auth,
            verify=False
        )

        job_complete = self.is_job_complete(response=response)
        while not job_complete:
            time.sleep(self.JOB_WAIT_SLEEP_TIME_SECONDS)
            # Note that, on success, a GET to the job redirects to the created or modified resource,
            # and we follow that redirect here.
            response = requests.get(
                url=url,
                auth=self.auth,
                verify=False
            )
            job_complete = self.is_job_complete(response=response)

        return response.json()

    @staticmethod
    def is_job_complete(response: Response) -> bool:
        """Determines if a job in the Package Repository service has completed."""
        if response.status_code >= 400:
            raise RepoError("Error: Request to get job returned status code {status_code}"
                            "with message {message}"
                            .format(status_code=response.status_code, message=response.text))

        if 'job' not in response.json() and response.status_code == 200:
            # Job completed and redirected us to the created or modified resource
            return True

        job = response.json()['job']
        job_status = job['status']
        if (job_status == 'PENDING' or job_status == 'RUNNING'):
            # Job is still running
            return False

        if job_status == 'FAILED':
            raise RepoError("Error: " + job['error']['message'])

        # Job is complete, and this type of job does not redirect
        return True

    # def _get_ssl_context_without_validation(self):
    #   """Function for getting an SSL context with SSL validation disabled. Useful
    #   if uploading a file hosted on the network in some situations"""
    #   context = ssl.create_default_context()
    #   context.check_hostname = False
    #   context.verify_mode = ssl.CERT_NONE
    #   return context

if __name__ == '__main__':
    # Disable the warning that is printed when we make calls through the requests library
    # (we disable SSL validation so this script can work if your SystemLink Server's certificate
    # isn't added to the trusted certificate store)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Uploader().run()