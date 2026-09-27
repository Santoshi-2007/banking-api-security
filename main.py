from fastapi import FastAPI, Header, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from oauth import router as oauth_router
import jwt
import time

app = FastAPI(title="Public Banking API")

bearer_scheme = HTTPBearer()

app.include_router(oauth_router, prefix="/oauth")

API_KEY = "FINTECH001_SECRET"

JWT_SECRET = "bank-demo-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "bank-auth-server"
JWT_AUDIENCE = "bank-api"

RATE_LIMIT = 5
RATE_WINDOW = 60

request_log = {}


def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )


def check_rate_limit(x_api_key: str):
    current_time = time.time()

    if x_api_key not in request_log:
        request_log[x_api_key] = []

    request_log[x_api_key] = [
        timestamp
        for timestamp in request_log[x_api_key]
        if current_time - timestamp < RATE_WINDOW
    ]

    if len(request_log[x_api_key]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )

    request_log[x_api_key].append(current_time)


def verify_jwt(
    credentials: HTTPAuthorizationCredentials,
    required_scope: str
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="JWT has expired"
        )

    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=401,
            detail="Invalid JWT issuer"
        )

    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=401,
            detail="Invalid JWT audience"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid JWT"
        )

    scope = payload.get("scope", "").split()

    if required_scope not in scope:
        raise HTTPException(
            status_code=403,
            detail="Insufficient scope"
        )

    return payload


@app.get("/")
def home():
    return {
        "message": "Welcome to the Public Banking API"
    }


@app.get("/accounts")
def get_accounts(
    x_api_key: str = Header(None, alias="X-API-Key"),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    verify_api_key(x_api_key)

    check_rate_limit(x_api_key)

    verify_jwt(
        credentials,
        "accounts:read"
    )

    return {
        "accounts": [
            {
                "account_id": "ACC001",
                "holder": "Rahul",
                "balance": 50000
            },
            {
                "account_id": "ACC002",
                "holder": "Priya",
                "balance": 75000
            }
        ]
    }


ACCOUNT_OWNERS = {
    "ACC001": "USER001",
    "ACC002": "USER002"
}


@app.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    x_api_key: str = Header(None, alias="X-API-Key"),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    verify_api_key(x_api_key)

    check_rate_limit(x_api_key)

    payload = verify_jwt(
        credentials,
        "accounts:read"
    )

    if account_id not in ACCOUNT_OWNERS:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    user_id = payload.get("sub")

    if ACCOUNT_OWNERS[account_id] != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this account"
        )

    accounts = {
        "ACC001": {
            "account_id": "ACC001",
            "holder": "Rahul",
            "balance": 50000
        },
        "ACC002": {
            "account_id": "ACC002",
            "holder": "Priya",
            "balance": 75000
        }
    }

    return accounts[account_id]


@app.get("/transactions")
def get_transactions(
    x_api_key: str = Header(None, alias="X-API-Key"),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    verify_api_key(x_api_key)

    check_rate_limit(x_api_key)

    verify_jwt(
        credentials,
        "transactions:read"
    )

    transactions = [
        {
            "transaction_id": "TXN001",
            "account_id": "ACC001",
            "amount": 5000,
            "type": "Credit",
            "date": "2026-09-27",
            "card_number": "4111111111111111",
            "customer_phone": "9876543210",
            "customer_address": "Mumbai, Maharashtra",
            "ip_address": "192.168.1.20"
        },
        {
            "transaction_id": "TXN002",
            "account_id": "ACC001",
            "amount": 1500,
            "type": "Debit",
            "date": "2026-09-26",
            "card_number": "4111111111111111",
            "customer_phone": "9876543210",
            "customer_address": "Mumbai, Maharashtra",
            "ip_address": "192.168.1.21"
        }
    ]

    safe_transactions = []

    for transaction in transactions:
        safe_transactions.append({
            "transaction_id": transaction["transaction_id"],
            "account_id": transaction["account_id"],
            "amount": transaction["amount"],
            "type": transaction["type"],
            "date": transaction["date"]
        })

    return {
        "transactions": safe_transactions
    }