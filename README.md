# Secure Public Banking API

A secure REST API prototype for exposing banking account and transaction data to third-party fintech partners.

This project demonstrates a layered security model using API Keys, OAuth 2.0, JWT, rate limiting, object-level authorization, and data minimization.

## Project Objective

Banks may need to expose account and transaction APIs to third-party fintech applications.

The API must allow authorized access while preventing:

- Unauthorized API access
- Unauthorized account access
- Excessive requests
- Token misuse
- Sensitive data exposure

## Security Architecture

```text
Fintech Partner
      |
      | API Key
      v
Partner Identification
      |
      v
Rate Limiting
      |
      v
OAuth 2.0 Authorization
      |
      | User Consent
      v
Authorization Code
      |
      v
JWT Access Token
      |
      v
JWT Validation
      |
      +-- Signature
      +-- Issuer
      +-- Audience
      +-- Expiration
      +-- Scope
      |
      v
Object-Level Authorization
      |
      v
Data Minimization
      |
      v
Banking REST API
Technologies Used
Python
FastAPI
Uvicorn
OAuth 2.0
JWT
PyJWT
Swagger / OpenAPI
Git
GitHub
API Key Authentication

Each fintech partner is identified using an API key.

Example:

X-API-Key: FINTECH001_SECRET

Invalid or missing API keys are rejected with:

401 Unauthorized

Example response:

{
  "detail": "Invalid or missing API key"
}
OAuth 2.0 Authorization

The project demonstrates a simplified authorization-code flow.

Fintech Application
        |
        v
Authorization Endpoint
        |
        v
User Consent
        |
        v
Authorization Code
        |
        v
Token Endpoint
        |
        v
JWT Access Token

The API supports scopes such as:

accounts:read
transactions:read

User consent is required before issuing the access token.

JWT Authentication

The access token is a signed JSON Web Token.

Important JWT claims include:

sub - User identifier
client_id - Fintech partner identifier
scope - Permissions
iss - Token issuer
aud - Intended API
exp - Expiration time
iat - Issued-at time

The resource server validates the JWT without making a database call for every request.

It validates:

JWT signature
Issuer
Audience
Expiration
Required scope

Expired tokens are rejected with:

401 Unauthorized
BOLA Protection

The API protects against Broken Object Level Authorization.

Example ownership:

ACC001 -> USER001
ACC002 -> USER002

If USER001 requests ACC001:

200 OK

If USER001 attempts to access ACC002:

403 Forbidden

Example response:

{
  "detail": "You are not authorized to access this account"
}

This ensures that having a valid JWT does not automatically grant access to every account.

Rate Limiting

The API implements a demonstration rate limit of:

5 requests per 60 seconds

After the limit is exceeded:

429 Too Many Requests

Example response:

{
  "detail": "Rate limit exceeded. Try again later."
}

This protects the API against excessive resource consumption.

Data Minimization

The transaction endpoint returns only the information required by the fintech application.

Returned fields include:

transaction_id
account_id
amount
type
date

Sensitive internal information such as:

card_number
customer_phone
customer_address
ip_address

is not returned to the API consumer.

This reduces the risk of excessive data exposure.

OWASP API Security Threat Mapping
Threat	Protection
Broken Object Level Authorization	Account ownership check
Unrestricted Resource Consumption	Rate limiting
Excessive Data Exposure	Data minimization
Broken Authentication	API Key + OAuth 2.0 + JWT
Token Misuse	JWT expiration and validation
Security Test Results
Test	Expected Result
Valid API request	200 OK
Missing API Key	401 Unauthorized
Missing JWT	401 Unauthorized
Expired JWT	401 Unauthorized
Unauthorized account access	403 Forbidden
Excessive requests	429 Too Many Requests
Sensitive fields in transaction response	Not exposed
Main API Endpoints
Method	Endpoint	Purpose
GET	/	API welcome message
GET	/oauth/authorize	OAuth authorization
POST	/oauth/token	Generate access token
GET	/accounts	Get accounts
GET	/accounts/{account_id}	Get individual account
GET	/transactions	Get transactions
Installation

Clone the repository:

git clone https://github.com/Santoshi-2007/banking-api-security.git

Enter the project directory:

cd banking-api-security

Create a virtual environment:

python -m venv venv

Activate the virtual environment on Windows:

venv\Scripts\activate

Install the required packages:

pip install fastapi uvicorn pyjwt
Run the Application

Start the server:

uvicorn main:app --reload

API:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Project Structure
banking-api-security/
│
├── main.py
├── oauth.py
├── .gitignore
└── README.md
Project Demonstration

The project demonstrates the following security flow:

API Key
   ↓
Rate Limiting
   ↓
OAuth 2.0
   ↓
User Consent
   ↓
Authorization Code
   ↓
JWT
   ↓
JWT Validation
   ↓
Scope Validation
   ↓
BOLA Protection
   ↓
Data Minimization
   ↓
Banking API
Important Note

This project is an educational prototype for demonstrating REST API security concepts.

It is not intended for handling real banking or financial data.

Production banking systems require additional security controls such as HTTPS/TLS, secure secret management, key rotation, audit logging, monitoring, distributed rate limiting, strong client authentication, security testing, and regulatory compliance.

Author
Santoshi Falle
B.Tech Computer Science and Engineering