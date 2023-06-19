from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.environ.get("OAUTH_SECRET_KEY")
ALGORITHM = os.environ.get("OAUTH_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("OAUTH_EXPIRE_MINUTES"))


def create_access_token(data: dict):
    
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
