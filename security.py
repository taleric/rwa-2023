import database
import models

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, status, HTTPException
from datetime import datetime, timedelta

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def hash_password(password):
    return password_context.hash(password)

async def authenticated(token):
    print(f'security.authenticated({token})')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f'jwt_payload: {payload}')
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await database.get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def login(username: str, password: str):
    user_db = await database.get_user(username, password)
    print(f'security.login({username},{password}): {user_db}')
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": user_db.username,
        "exp": datetime.utcnow() + access_token_expires
    }
    access_token = jwt.encode(access_token_data, SECRET_KEY, algorithm=ALGORITHM)
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}