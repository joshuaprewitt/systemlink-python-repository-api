
from systemLink_package_repo_client import SystemLink_Package_Repo_Client
import asyncio

s_Host= "http://localhost:9090"  # http(s)://server:port 
s_APIKey = "KpTb6ujPqMq3bH-4k9g2uxyYXNraR0oPhE_40fIeKP"   # APIKey secret generated from method POST /keys
s_FeedName = s_Name = "My Feed" # feed name
s_Feed_Description = "my description" # feed description
s_Platform ="windows"  # platform for which the feed is created 
s_Workspace_ID = "5e680020-6471-4896-b4dc-e136173c7bf6" # ID of the workspace to which the feed belongs. See readme file
s_Path = r"C:\yourpath\yourpackagename.nipkg" # path of the package to be added to the feed

SL_Repo_Client =SystemLink_Package_Repo_Client(s_Host, s_APIKey)


#creates feeds and upload packages
jid = asyncio.run(SL_Repo_Client.create_feed(s_Name,s_Feed_Description, s_Platform, s_Workspace_ID))
print('The create feed  job id is', jid)
feedid = asyncio.run(SL_Repo_Client.get_feed_id(jid))
print('The created feed id is', feedid)
jid = asyncio.run(SL_Repo_Client.upload_package(s_Path))
print('The package job id is', jid)
packageid = asyncio.run(SL_Repo_Client.get_package_id(jid))
print('The package  id is', packageid)
jid = asyncio.run(SL_Repo_Client.add_package_to_feed(packageid,feedid))
print('Upload was successful')
