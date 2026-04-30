from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from databricks import sql
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

def get_connection():
    conn = sql.connect(
        # server_hostname=server_hostname,
        # http_path=http_path,
        # access_token=DATABRICKS_TOKEN
        
        server_hostname=os.getenv("SERVER_HOSTNAME"),
        http_path=os.getenv("HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )
    return conn

class AddMovie(BaseModel):
    id: int
    title: str
    release_year: int
    hero: str
    box_office: float

@app.post("/movie/add")
def add_movie(am: AddMovie):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("insert into movie_data.default.marvel_movies(id, title, release_year, hero, box_office_billions) values (?,?,?,?,?)", (am.id, am.title, am.release_year, am.hero, am.box_office))
    conn.commit()
    conn.close()
    return {"message": "Movie Added"}

@app.get("/movie/{hero}")
def fetch_movie_by_hero(hero: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "select * from movie_data.default.marvel_movies where hero = ?",
        (hero,)
    )
    rows = cursor.fetchall()

    # 👇 Get column names
    columns = [col[0] for col in cursor.description]

    # 👇 Convert rows to list of dicts
    data = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return data
