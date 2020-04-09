from uploader import Uploader
import requests
from os import listdir
from os.path import isfile, join

package_uploader = Uploader()

package_uploader.set_server_parameters(systemlink_server_url='http://localhost/', username='admin', password='password')

def get_feed_id(feeds_json, feed_name):
    for feed in feeds_json['feeds']:
        #print(feed)
        if feed['feedName'] == feed_name:
            return feed['id']
    return None

response = package_uploader.get_feeds()
feed_name = 'Test Feed'
feed_id = get_feed_id(response.json(), feed_name)

if feed_id == None:
    package_uploader.create_feed(feed_name, 'Matts test Feed')
else:
    print('Feed already exists!')
    
mypath = './packages'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print(onlyfiles)

files_to_upload = []
for file in onlyfiles:
    if file.endswith('.nipkg'):
        files_to_upload.append(file)
print(files_to_upload)

for file in files_to_upload:
    my_file = './packages/{}'.format(file)
    package_uploader.upload_and_add(filename=my_file, feed_id=feed_id)