# systemlink-python-repository-api

Python API for publishing packages to a SystemLink Server

# Overview

The following Python API can be used to automate publishing packages (.nipkg or .ipk) from a CI like Jenkins.  Below are a few examples on how to use it.
 
You can call it from the command line like:
```
python.exe uploader.py --filename C:\Users\josh\Documents\repo_tester\ni-test-package_1.0.0-12_windows_x64.nipkg --feedId 5b69f2bbe0d644592c8963aa --serverUrl https://localhost:9091 --username admin --password test
```

Other python programs can import it as a module and just call upload_and_add():
```
from uploader import Uploader
    uploader = Uploader(systemlink_server_url='https://localhost:9091', username='admin', password='test')
    uploader.upload_and_add(filename='C:\\Users\\josh\\Documents\\repo_tester\\ni-test-package_1.0.0-12_windows_x64.nipkg', feed_id='5b69f2bbe0d644592c8963aa')
```
