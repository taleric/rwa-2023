from fastapi import Depends, FastAPI, status, Body, HTTPException
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


@app.post("/register", response_model=models.UserIn)
async def register(user: models.UserIn = Body(...)):
    hashed_password = security.hash_password(user.password)
    user_db = models.UserDb(
        _id=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    print(f'user_db: = {user_db}')

    new_user = await database.db["users"].insert_one(jsonable_encoder(user_db))
    created_user = await database.db["users"].find_one({"_id": new_user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


@app.get("/me", response_model=models.UserDb)
async def get_me(current_user: models.UserDb = Depends(authenticated)):
    return jsonable_encoder(current_user)


### API: Posts ###

@app.get("/posts/", response_model=List[models.PostDb])
async def get_all_pposts(current_user: models.UserDb = Depends(authenticated)):
    return await database.fetch_all_posts()


@app.get("/posts/{post_id}", response_model=models.PostDb)
async def get_single_post(post_id: str, current_user: models.UserDb = Depends(authenticated)):
    post = await database.fetch_one_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts/")
async def create_post(current_user: models.UserDb = Depends(authenticated), post_in: models.PostIn = Body(...)):
    created_post = await database.create_post(post_in)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_post)


@app.put("/posts/{post_id}", response_model=models.PostDb)
async def update_post(post_id: str, post: models.PostIn, current_user: models.UserDb = Depends(authenticated)):
    post_data = await database.fetch_one_post(post_id)
    if not post_data:
        raise HTTPException(status_code=404, detail="Post not found")
    await database.update_post(post_id, post.dict())
    return await database.fetch_one_post(post_id)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, current_user: models.UserDb = Depends(authenticated)):
    post_data = await database.fetch_one_post(post_id)
    if not post_data:
        raise HTTPException(status_code=404, detail="Post not found")
    await database.delete_post(post_id)
    return {"message": "Post has been deleted"}


### API: Comments ###

@app.get("/posts/{post_id}/comments", response_model=List[models.CommentDb])
async def get_comments(post_id: str, current_user: models.UserDb = Depends(authenticated)):
    return await database.fetch_comments_by_post(post_id)


@app.post("/posts/{post_id}/comments")
async def add_comment(post_id: str, comment_in: models.CommentIn = Body(...), current_user: models.UserDb = Depends(authenticated)):
    post_data = await database.fetch_one_post(post_id)
    if not post_data:
        raise HTTPException(status_code=404, detail="Post not found")
    created_comment = await database.add_comment(post_id, current_user.username, comment_in)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_comment)


@app.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, current_user: models.UserDb = Depends(authenticated)):
    post_data = await database.fetch_one_post(post_id)
    if not post_data:
        raise HTTPException(status_code=404, detail="Post not found")
    await database.delete_comment(comment_id)
    return {"message": "Comment has been deleted"}
