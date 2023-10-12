import models
import security
import uuid

import os
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder


async def init_db():
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://app:1DISjZiUKzmkY8QY@cluster0.mjx90ic.mongodb.net/?retryWrites=true&w=majority")
    global db
    db = mongodb_client.tododb_v2
    print("database.init_db(): Connected to the MongoDB database!")


async def get_user(username: str, password: str = None):
    document = await db["users"].find_one({"_id": username})
    print(f'database.get_user({username}, {password}): {document}')
    if document:
        user = models.UserDb(**document)
        if (password):
            if (security.verify_password(password, user.hashed_password)):
                return user
        else:
            return user


async def fetch_all_posts():
    return await db["posts"].find().to_list(100)


async def fetch_one_post(post_id: str):
    return await db["posts"].find_one({"_id": post_id})


async def create_post(post_in: models.PostIn):
    post_db = models.PostDb(
        _id=str(uuid.uuid4()),
        title=post_in.title,
        slug=post_in.slug,
        content=post_in.content,
        published=post_in.published
    )
    new_post = await db["posts"].insert_one(jsonable_encoder(post_db))
    return await db["posts"].find_one({"_id": new_post.inserted_id})


async def update_post(post_id: str, post: dict):
    try:
        await db["posts"].update_one({"_id": post_id}, {"$set": post})
    except Exception as e:
        print(f"Error updating post: {e}")


async def delete_post(post_id: str):
    await db["posts"].delete_one({"_id": post_id})


async def fetch_comments_by_post(post_id: str):
    return await db["comments"].find({"post_id": post_id}).to_list(100)


async def add_comment(post_id: str, username: str, comment_in: models.CommentIn):
    comment_db = models.CommentDb(
        _id=str(uuid.uuid4()),
        post_id=post_id,
        username=username,
        comment=comment_in.comment
    )
    new_comment = await db["comments"].insert_one(jsonable_encoder(comment_db))
    return await db["comments"].find_one({"_id": new_comment.inserted_id})


async def delete_comment(comment_id: str):
    await db["comments"].delete_one({"_id": comment_id})
