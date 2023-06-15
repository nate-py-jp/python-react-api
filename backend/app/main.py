from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine
from dotenv import load_dotenv
import os
from .routers.user import router as user_router
from .routers.post import router as post_router
from .routers.auth import router as auth_router


load_dotenv()  # Load environment variables from .env file

db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)
app.include_router(post_router)
app.include_router(auth_router)

# connect to postgres for direct sql queries
while True:
    try:
        conn = psycopg2.connect(
            host = db_host, 
            database=db_name, 
            user=db_username, 
            password=db_password, 
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("db conn OK!")
        break
    except Exception as error:
        print(f"error in getting conn:", error)


# boilerplate to configure CORS settings to let fastapi calls work from browswer with React
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)