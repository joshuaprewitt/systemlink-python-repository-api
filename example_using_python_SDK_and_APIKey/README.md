# External Api Keys
External Api Keys are needed when a regular user login is not possible or inconvenient. 
This is typically the
case for automatic triggered scripts or devices.
# Org Modeling
Org Modeling allows to create Api Keys using the Rest interface.

visit <host>/niapis/niapis/?urls.primaryName=Auth Service
  
# Create a policy
Create a new policy for a particular workspace based on a template:
POST /policies

````
{
  "name": "string",
  "type": "default",
  "templateId": "365ecbd3-6675-445c-a038-7ed3859f8419",
  "workspace": "8b27a388-6d7e-44d7-8f28-c92f47fbc7f6"
}
````
templateId 

You can get be the templateId of a built-in role or an ad-hoc created one(e.g. Data Maintainer). 
It's very easy to "sniff" the id in
the Browser's dev tools.
1. Press F12 to open DevTools and switch to Network Tab
2. Visit the Security UI -> Roles
3. Edit "Data Maintainer" and retrieve its id from the network tab
4. Alternatively, you can use GET /policy-templates to query available templates

workspaceId

workspaceId that the policy should be act upon. WorkspaceIds can be retrieved using the
following Rest call:
GET <host>/niuser/v1/workspaces?take=50
The response contains a property "id" that is our policyId needed to create the Api Key. If access is needed
for multiple workspaces, repeat the step and copy all retrieved policyIds.

# Create Api Key
Create the external Api Key.
POST /keys

````
{
 "name": "test_key",
 "policyIds": [
 "<policyId>"
 ],
 "properties": {}
}
The response contains a property "secret". This is the generated Api Key. The secret will never show up again
and must be carefully stored. The created Api Key is associated with the currently logged-in user 

````
