import models
import security
import uuid

import os
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder

async def init_db():
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
    global db
    db = mongodb_client.tododb_v2
    print("database.init_db(): Connected to the MongoDB database!")


async def get_user(username: str, password: str = None):
    document = await db["users"].find_one({"_id": username})
    print(f'database.get_user({username}, {password}): {document}')
    if document:
        user = models.UserDb(**document)
        if(password):
            if(security.verify_password(password, user.hashed_password)):
                return user
        else:
             return user
        
async def create_todo(current_user: models.UserDb, todo_in: models.TodoIn):
    todo_db = models.TodoDb(
        _id = str(uuid.uuid4()),
        username = current_user.username,
        title = todo_in.title,
        description = todo_in.description
    )

    new_todo = await db["todos"].insert_one(jsonable_encoder(todo_db))
    return await db["todos"].find_one({"_id": new_todo.inserted_id})

async def list_todos(current_user: models.UserDb):
    todos = await db["todos"].find({"username": current_user.username}).to_list(100)
    return todos
