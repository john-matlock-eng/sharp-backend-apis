import os
import boto3
import logging
import requests
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cognito settings
COGNITO_REGION = os.getenv('AWS_REGION')
USER_POOL_ID = os.getenv('USER_POOL_ID')
APP_CLIENT_ID = os.getenv('APP_CLIENT_ID')
COGNITO_JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class CognitoService:
    def __init__(self):
        self.region = COGNITO_REGION
        self.user_pool_id = USER_POOL_ID
        self.app_client_id = APP_CLIENT_ID
        self.jwks_url = COGNITO_JWKS_URL

    def get_jwks(self):
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            return response.json()['keys']
        except Exception as e:
            logger.error(f"Error fetching JWKS: {e}")
            raise HTTPException(status_code=500, detail="Error fetching JWKS")

    def validate_token(self, token: str):
        try:
            jwks = self.get_jwks()
            unverified_headers = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks:
                if key["kid"] == unverified_headers["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=self.app_client_id,
                    issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
                )
                return payload
            else:
                logger.error("Unable to find appropriate key")
                raise HTTPException(status_code=400, detail="Invalid token")
        except JWTError as e:
            logger.error(f"JWT error: {e}")
            raise HTTPException(status_code=400, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(status_code=500, detail="Token validation error")

    def extract_claims(self, token: str):
        payload = self.validate_token(token)
        return {
            "username": payload.get("username"),
            "email": payload.get("email"),
            "sub": payload.get("sub")
        }

# Dependency
def get_cognito_service():
    return CognitoService()

def get_current_user(token: str = Depends(oauth2_scheme), cognito_service: CognitoService = Depends(get_cognito_service)):
    return cognito_service.extract_claims(token)
