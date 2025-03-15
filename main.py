from inspect import trace
import traceback
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
import sqlite3
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
    conn = sqlite3.connect("products_db.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def initialize_database(db_name):
    if not os.path.exists(db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database '{db_name}' and table 'products' created successfully.")
    else:
        print(f"Database '{db_name}' already exists.")

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
async def create_product(id: str, name: str, price: float, description: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO products (id, name, price, description) VALUES (?, ?, ?, ?)",
                    (id, name, price, description))
        conn.commit()
        conn.close()
        
        return {"message": "Product added successfully", 'name':name, 'price':price, 'desc':description}
    except sqlite3.IntegrityError:
        return {"message": f'Duplicate product id: {id}'}
    except:
        print(traceback.format_exc())
        return {'message': traceback.format_exc()}

if __name__ == "__main__":
    initialize_database("products_db.sqlite")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8036,
        reload=True
    )
