# sample-issuer-app
The sample Issuer application demonstrates the capability of Wipro’s Issuer. Wipro’s Issuer can be used to issue credential. Different stakeholders involved are:
- Identity Wallet 
- Issuer platform and
- Sample Issuer application

Issuer is available at: https://futurebankapi.wiprobc.com/swagger-ui.html 
Through the sample issuer application, credential Issuance happens in the following steps:
1.	Create connection invitation
     -	It takes user email id as input and sends invitation  to this email address as QR code. The API used for this is: 
     -	https://futurebankapi.wiprobc.com/swagger-ui.html#connections-controller/, POST /submit
2.	Holder should scan this   QR code to establish connection with Issuer
3.	Create schema. For schema creation API used is: https://futurebankapi.wiprobc.com/swagger-ui.html#/schema-controller, POST /api/schema/createSchema. By default schema is created with the following attributes:
    - Name,
    - Email,
    - SPOC_Email
    - Credential_Valid_From,
    - Credential_Valid_Till
4. Issue Credential: This happens in 3 steps
   - Issuers sends credential offer to Holder. The REST API used for credential offer is: https://futurebankapi.wiprobc.com/swagger-ui.html#/credentials-controller/, POST
/api/credentialoffer
   - Once Holder receives the offer, holder accepts and sends credential request 
   - After receiving credential request from holder, credential is issued with API: https://futurebankapi.wiprobc.com/swagger-ui.html#/credentials-controller/, POST /api/issue-credential/records/{credential_exchange_id}/issue
![Issue Credential Flow](diagrams/cred_iss_seq.jpg)
