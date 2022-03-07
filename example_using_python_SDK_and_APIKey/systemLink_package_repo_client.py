from systemlink.clients.nirepo.api_client import ApiClient
from  systemlink.clients.nirepo.configuration import Configuration 
from systemlink.clients.nirepo.api.feeds_api import FeedsApi
from  systemlink.clients.nirepo.models.feed_data import FeedData
from systemlink.clients.nirepo.api.packages_api import PackagesApi
from systemlink.clients.nirepo.api.jobs_api import JobsApi
from systemlink.clients.nirepo.models.package_references_object import PackageReferencesObject
import asyncio


class SystemLink_Package_Repo_Client:
    def __init__(self, host, apikey) -> None:
        self.Host= host
        self.ApiKey= apikey
        ########## Login with username/password ###############
        #self.Config = Configuration(host = self.Host + "/nirepo", username='admin', password = 'admin')
        ########## Login with  APIkey           ###############
        self.Config = Configuration(host = self.Host + "/nirepo", api_key={'x-ni-api-key':self.ApiKey})
        self.Config.verify_ssl=False

    def __deinit__(self) -> None:
        pass

    async  def create_feed(self, name, description, platform, workspace_id):
        Api_Client = ApiClient(self.Config)
        Feed_Api_Obj = FeedsApi(Api_Client)
        Feed_Data = FeedData(feed_name= name, name=name, description=description, platform=platform, workspace=workspace_id, local_vars_configuration=None)
        job_id= None
        job_id = await Feed_Api_Obj.create_feed(async_req = False, feed_data=Feed_Data)
        await Api_Client.close()
        return job_id.to_dict()['job_id']
            
    async def get_feed_id(self,job_id):
        Api_Client = ApiClient(self.Config)
        Jobs_Api_Obj = JobsApi(Api_Client)
        job_details = await Jobs_Api_Obj.list_jobs(id=job_id,_preload_content=True,async_req=False)
        await Api_Client.close()
        job_details= job_details.to_dict()
        feed_id = job_details['jobs'][0]['resource_id']
        return feed_id
    

    async  def list_feeds(self):
        Api_Client = ApiClient(self.Config)
        Feed_Api_Obj = FeedsApi(Api_Client)
        feeds = await Feed_Api_Obj.list_feeds(async_req = False)
        await Api_Client.close()
        return feeds
    
    async  def delete_feed(self,feed_id):
        Api_Client = ApiClient(self.Config)
        Feed_Api_Obj = FeedsApi(Api_Client)
        job_id = await Feed_Api_Obj.delete_feed(feed_id,async_req = False)
        await Api_Client.close()
        return job_id
            

    async def upload_package(self,filename):
        Api_Client = ApiClient(self.Config)
        Package_Api_Obj = PackagesApi(Api_Client)
        job_details = await Package_Api_Obj.upload_package(filename,should_overwrite=True,async_req = False)
        job_details = job_details.to_dict()
        job_id = job_details['job_ids'][0]
        await Api_Client.close()
        return job_id


    async def get_package_id(self,job_id):
        Api_Client = ApiClient(self.Config)
        Jobs_Api_Obj = JobsApi(Api_Client)
        job_details = await Jobs_Api_Obj.list_jobs(id=job_id,_preload_content=True,async_req=False)
        job_details= job_details.to_dict()
        package_id = job_details['jobs'][0]['resource_id']
        await Api_Client.close()
        return package_id

    
    async def add_package_to_feed(self,package_id,feed_id):
        Api_Client = ApiClient(self.Config)
        Package_Api_Obj = PackagesApi(Api_Client)
        list_packages = []
        list_packages.append(package_id)
        Package_Ref_Obj = PackageReferencesObject( package_references=list_packages)
        jobid = await Package_Api_Obj.add_package_references(feed_id,package_references= Package_Ref_Obj, async_req=False)
        await Api_Client.close()
        return jobid   
            

