# sample-issuer-app
The sample Issuer application demonstrates the capability of Wipro’s Issuer. Wipro’s Issuer can be used to issue credential. Different stakeholders involved are:
- Identity Wallet 
- Issuer platform and
- Sample Issuer application

Issuer is available at: https://futurebankapi.wiprobc.com/swagger-ui.html 
Through the sample issuer application, credential Issuance happens in the following steps:
1.	 Create connection invitation
-	It takes user email id as input and sends invitation  to this email address as QR code
2.	Holder should scan this   QR code to establish connection with Issuer
3.	Create schema, by default schema is created with the following attributes:
    Name,
    Email,
    SPOC_Email
    Credential_Valid_From,
    Credential_Valid_Till
4. 
