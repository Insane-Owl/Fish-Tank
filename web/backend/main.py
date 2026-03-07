import sqlite3

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()


class SensorReading(BaseModel):
    temperature: float
    ph: float
    tds: float


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    conn = sqlite3.connect("fishtank.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            ph REAL,
            tds REAL
        )
        """
    )
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect("fishtank.db")
    conn.row_factory = sqlite3.Row  # makes SQLite return dictionaries instead of lists
    try:
        yield conn
    finally:
        conn.close()


@app.get("/api/sensors/latest")
def get_latest_item(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No data available yet")
    return dict(row)


@app.get("/api/sensors/history")
def get_sensor_history(limit: int = 60, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?", (limit,)
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@app.post("/api/sensors")
def add_item(item: SensorReading, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO sensor_data (temperature, ph, tds) VALUES (?, ?, ?)",
        (item.temperature, item.ph, item.tds),
    )
    db.commit()

    return {"message": "Success"}


init_db()
