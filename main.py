from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI()
DB_NAME = "finance_tracker.db"


# ------------------------
# Helper Function
# ------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# ------------------------
# Models
# ------------------------
class Friend(BaseModel):
    name: str


class Category(BaseModel):
    name: str
    type: str
    has_friend: int


class Transaction(BaseModel):
    date: str
    category_id: int
    amount: float
    note: Optional[str] = None
    friend_id: Optional[int] = None


# ------------------------
# Categories APIs
# ------------------------
@app.get("/categories")
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/categories")
def add_category(category: Category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categories (name, type, has_friend) VALUES (?, ?, ?)",
        (category.name, category.type, category.has_friend)
    )
    conn.commit()
    conn.close()
    return {"message": "Category added"}


@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()
    return {"message": "Category deleted"}


# ------------------------
# Friends APIs
# ------------------------
@app.get("/friends")
def get_friends():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM friends")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/friends")
def add_friend(friend: Friend):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO friends (name) VALUES (?)", (friend.name,))
        conn.commit()
    except:
        raise HTTPException(status_code=400, detail="Friend already exists")
    finally:
        conn.close()
    return {"message": "Friend added"}


@app.delete("/friends/{friend_id}")
def delete_friend(friend_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM friends WHERE id=?", (friend_id,))
    conn.commit()
    conn.close()
    return {"message": "Friend deleted"}


# ------------------------
# Transactions APIs
# ------------------------
@app.get("/transactions")
def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.date, c.name, c.type, t.amount, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/transactions")
def add_transaction(tx: Transaction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO transactions (date, category_id, amount, note) VALUES (?, ?, ?, ?)",
        (tx.date, tx.category_id, tx.amount, tx.note)
    )

    tx_id = cursor.lastrowid

    if tx.friend_id:
        cursor.execute(
            "INSERT INTO transaction_friends (transaction_id, friend_id) VALUES (?, ?)",
            (tx_id, tx.friend_id)
        )

    conn.commit()
    conn.close()
    return {"message": "Transaction added"}