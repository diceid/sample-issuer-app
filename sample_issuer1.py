import asyncio
from random import randint
from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)
import time
import os


schema_attributes = {}

async def check_existing_connection_id(issuer_url, auth_code):
    conn_id = input ("Enter connection id: ")
    path="/api/connection/"
    print("Getting connection infromation...\n")
    headers = {
                'Authorization': 'Bearer ' + auth_code
               }

    print ("request url = ", issuer_url  + path + conn_id)
    async with ClientSession() as session:
        async with session.request("GET", issuer_url + path + conn_id, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(
                    f"Error response code {resp.status}"
                )
            conn_resp=await resp.json()
            state=conn_resp["state"]
            print(f"Connection id= {conn_id}, Connection state= {state}\n")
            if state != "active":
                raise Exception(
                    f"Connection is not in active state"
                )
    return conn_id

async def print_oob_connection_invitation(issuer_url, auth_code):
    conn_id=None
    path="/submit"
    emailId=input("Enter your emailId: ")
    print("Creating connection invitation...\n")
    params = {
    			"emailId": emailId
    	    }
    headers = {
                'Authorization': 'Bearer ' + auth_code
            }
    async with ClientSession() as session:
        async with session.request("POST", issuer_url + path, params=params, headers=headers) as resp:
            if resp.status != 201:
                raise Exception(
                    f"Error response code {resp.status}"
                )
            conn_info=await resp.text()
            idx=conn_info.find("id=")+4
            conn_id=conn_info[idx:idx+36]
            
            print("Email is sent with invitation link, please click on the link and scan the QR code with DICE wallet\n")

    return conn_id     


async def use_existing_schema(issuer_url, auth_code):
    schema_id= input ("Enter schema id: ")
    seqno=None
    headers = {
                'Authorization': 'Bearer ' + auth_code
            }
    print("Fetching schema information...\n")
    path="/api/schema/"

    async with ClientSession() as session:
        async with session.request("GET", issuer_url + path + schema_id, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(
                    f"Error response code {resp.status}"
                )
            conn_resp=await resp.json()
            seqno=conn_resp["seq_num"]
            schema_attributes=conn_resp["attributes"]
            print(f"Schema:\n{schema_id}, Schema SeqNo= {seqno}, Schema attributes= {schema_attributes}\n")
    return schema_id,seqno,schema_attributes
        


async def create_schema(issuer_url, auth_code):
    schema_id=None
    seqno=None
    print("Creating schema...\n")
    path="/api/schema/"
    payload = {
    			
                "attributes": {
                                "Name":"text",
                                "Age":"text",
                                "PAN":"text",
                                "PostalAddress":"text"
                            },
                "schema_name": "schema_name" + str(randint(0,100)),
                "schema_version": "1.0"                                
    	    }
   
    headers = {
                'Authorization': 'Bearer ' + auth_code
            }
            

    async with ClientSession() as session:
        async with session.request("POST", issuer_url + path, json=payload, headers=headers) as resp:
            if resp.status != 201:
                raise Exception(
                    f"Error response code {resp}"
                )
            schema_info = await resp.json()
            schema_id=schema_info["schema_id"]
        async with session.request("GET", issuer_url + path + schema_id, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(
                    f"Error response code {resp.status}"
                )
            conn_resp=await resp.json()
            seqno=conn_resp["seq_num"]
            schema_attributes=conn_resp["attributes"]
            print(f"Schema created:\n{schema_id}, Schema SeqNo= {seqno}, Schema attributes= {schema_attributes}\n")
        
    return schema_id,seqno,schema_attributes


async def send_credential(issuer_url, auth_code, conn_id, schema):
    print("Sending credential...\n")
    path="/api/credentialoffer"
    contents=schema[0].split(":")
    cred_def_id=contents[0]+":3:CL:"+schema[1]+":default"
    print("cred_def_id:",cred_def_id)
    data=schema[2]
    attributes=[]
    attributes=[value for attribute in data for value in attribute.values()]
    del attributes[1::2]
    print("schema attributes: ",attributes)
    dictionary=dict()
    res=[]  
    for i in attributes:
        x=input("Enter your {} : ".format(i))
        dictionary["name"]=i
        dictionary["value"]=x
        res.append(dictionary.copy())
    
    conn_id=input("Enter connection id: ")
    valid_from = int(time.time())
    valid_to = valid_from + 31536000
    payload = {
                    "auto_issue": "true",
                    "comment": "string",
                    "connection_id": conn_id,
                    "cred_def_id": cred_def_id,
                    "credential_preview": {
                        "@type": "string",
                        "attributes": res
                    }
                }
    headers = {
                'Authorization': 'Bearer ' + auth_code
            } 
    async with ClientSession() as session:
        async with session.request("POST", issuer_url + path, json=payload, headers=headers) as resp:
            if resp.status != 201:
                raise Exception(
                    f"Error response code {resp}"
                )
  


async def main():
    conn_id=None
    #issuer_url = "https://futurebankapi.diceid.com"
    issuer_url = "https://futureapi.diceid.com"
    auth_code = os.getenv("AUTHORIZATION_CODE",None)
    if(auth_code is None):
        auth_code = input("Input Authorization Code: ")
    print("\n")
    options = (
            "    Connection\n"
            "    (1a) Create New Connection\n"
            "    (1b) Use Existing Connection\n"
            "    Schema\n"
            "    (2a) Create New Schema\n"
            "    (2b) Use Existing Schema\n"
            "    (3) Send Credential to Holder\n"
            "    (X) Exit\n"
        )
    
    
    while True:
        print(options)
        Res=input("[1a /1b / 2a / 2b / 3 / X]\n")
        if Res is None or Res in "xX":
            break

        elif Res == "1a":
            conn_id = await print_oob_connection_invitation(issuer_url, auth_code)
        elif Res == "1b":
            conn_id = await check_existing_connection_id(issuer_url, auth_code)
        
        elif Res == "2a":
            schema = await create_schema(issuer_url, auth_code)   
        
        elif Res == "2b":
            schema = await use_existing_schema(issuer_url, auth_code)   

        elif Res == "3" and conn_id is not None and schema is not None:
            await send_credential(issuer_url, auth_code,conn_id, schema)  


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    os._exit(1)
