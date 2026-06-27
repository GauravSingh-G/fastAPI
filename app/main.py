from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import models, schemas
from database import engine, get_db
from routers import users, posts
from dotenv import load_dotenv
import os

load_dotenv()




models.Base.metadata.create_all(bind = engine)

try:
    db_conn = psycopg2.connect(host = os.getenv("DB_HOST"), database = os.getenv("DB_DATABASE"), user = os.getenv("DB_USER"), password = os.getenv("DB_PASSWORD"), cursor_factory=RealDictCursor)

    db_cursor = db_conn.cursor()

    print("Connection to Database Successfull...")
except Exception as e:
    print("Connection to Database Failed!")
    print("Error: ", e)


#----------------------------------------------------------------------

app = FastAPI()

#-----------------------------------------------------------------------

app.include_router(users.router)
app.include_router(posts.router)



@app.get('/')
def root():
    return {'message': 'Hello World!'}




