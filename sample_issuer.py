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


async def print_oob_connection_invitation(issuer_url, auth_code):
    conn_id=None
    print("Creating connection invitation...\n")
    path="/submit"
    emailId=input("Enter your emailId:")
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
            
            print(f"Connection Invitation Created:{conn_id} !!!!!!\n")
            print("::::::Go to given mail id for QR Code:::::\n")

    return conn_id     


async def create_schema(issuer_url, auth_code):
    schema_id=None
    seqno=None
    print("Creating schema...\n")
    path="/api/schema/"
    payload = {
    			
                "attributes": {
                                "Name":"text",
                                "Email":"text",
                                "SPOC_Email":"text",
                                "Credential_Valid_From":"text",
                                "Credential_Valid_Till":"text"
                            },
                "schema_name": "name" + str(randint(0,100)),
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
            print(f"Schema_Info: id= {schema_id} , SeqNo= {seqno}\n")
        
    return schema_id,seqno


async def send_credential(issuer_url, auth_code, conn_id, schema):
    print("Sending credential...\n")
    path="/api/credentialoffer"
    contents=schema[0].split(":")
    cred_def_id=contents[0]+":3:CL:"+schema[1]+":default"
    print("cred_def_id:",cred_def_id)
    payload = {
                    "auto_issue": "true",
                    "comment": "string",
                    "connection_id": conn_id,
                    "cred_def_id": cred_def_id,
                    "credential_preview": {
                        "@type": "string",
                        "attributes": [
                        {
                            "name": "Name",
                            "value": "John"
                        },
                        {
                            "name": "Email",
                            "value": "abc@gmail.com"
                        }
                        ]
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
            schema_info = await resp.json()
            print(f"Schema_Info: {schema_info}\n")
  


async def main():
    conn_id=None
    issuer_url = "https://futurebankapi.wiprobc.com"
    auth_code = input("Input Authorization Code: ")
    print("\n")
    options = (
            "    (1) Create Connection\n"
            "    (2) Create Schema\n"
            "    (3) Send Credential to Holder\n"
            "    (X) Exit\n"
        )
    
    
    while True:
        print(options)
        Res=input("[1 / 2 / 3 / X]\n")
        if Res is None or Res in "xX":
            break

        elif Res == "1":
            conn_id = await print_oob_connection_invitation(issuer_url, auth_code)
        
        elif Res == "2":
            schema = await create_schema(issuer_url, auth_code)   

        elif Res == "3" and conn_id is not None and schema is not None:
            await send_credential(issuer_url, auth_code,conn_id, schema)  


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    os._exit(1)