from fastapi import Depends, FastAPI, status, Body
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import List

import models
import database
import security

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.on_event("startup")
async def startup_db_client():
    await database.init_db()


### API: Auth & Users ###

async def authenticated(token: str = Depends(oauth2_scheme)):
    return await security.authenticated(token)

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    return await security.login(form.username, form.password)

@app.post("/users", response_model=models.UserIn)
async def create_user(user: models.UserIn = Body(...)):
    hashed_password = security.hash_password(user.password)
    user_db = models.UserDb(
        _id = user.username,
        email = user.email,
        hashed_password = hashed_password
    )

    print(f'user_db: = {user_db}')

    new_user = await database.db["users"].insert_one(jsonable_encoder(user_db))
    created_user = await database.db["users"].find_one({"_id": new_user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


@app.get("/users/me", response_model=models.UserDb)
async def get_me(current_user: models.UserDb = Depends(authenticated)):
    return jsonable_encoder(current_user)


### API: Todo ###

@app.post("/todos", response_model=models.TodoDb)
async def create_todo(current_user: models.UserDb = Depends(authenticated), todo_in: models.TodoIn = Body(...)):
    created_todo = await database.create_todo(current_user, todo_in)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_todo)

@app.get("/todos", response_model=List[models.TodoDb])
async def list_todos(current_user: models.UserDb = Depends(authenticated)):
    todos = await database.list_todos(current_user)
    return todos