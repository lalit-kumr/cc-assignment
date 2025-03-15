from inspect import trace
import traceback
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
import psycopg2
from psycopg2 import sql
from pydantic import BaseModel

# Create the FastAPI app
app = FastAPI()

# Initialize the Jinja2 template engine
templates = Jinja2Templates(directory="templates")

# Define the Pydantic model for request validation
class Product(BaseModel):
    name: str
    price: float
    description: str

# Function to get a database connection
def get_db_connection():
    # DATABASE_URL = "postgresql://database1_9tum_user:1K36dHfeeou8j7Mox0XTk3agwXklB5cF@dpg-cvas25fnoe9s73fepq10-a.singapore-postgres.render.com/database1_9tum"
    DATABASE_URL = "postgresql://database1_9tum_user:1K36dHfeeou8j7Mox0XTk3agwXklB5cF@dpg-cvas25fnoe9s73fepq10-a/database1_9tum"
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Initialize the database
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully.")

# Route to serve the HTML form
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/products/")
async def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all products
        cursor.execute("SELECT id, name, price, description FROM products")
        products = cursor.fetchall()
        conn.close()

        # Convert the database rows into a list of dictionaries
        product_list = [
            {"id": row[0], "name": row[1], "price": row[2], "description": row[3]}
            for row in products
        ]

        return product_list

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Create product endpoint (POST /products/)
@app.post("/products/")
async def create_product(id: int, name: str, price: float, description: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO products (id, name, price, description) VALUES (%s, %s, %s, %s)",
                    (id, name, price, description))
        conn.commit()
        conn.close()
        
        return {"message": "Product added successfully", 'name': name, 'price': price, 'desc': description}
    except psycopg2.IntegrityError:
        return {"message": f'Duplicate product id: {id}'}
    except:
        print(traceback.format_exc())
        return {'message': traceback.format_exc()}

if __name__ == "__main__":
    initialize_database()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8036,
        reload=True
    )
