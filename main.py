from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Product
from database import SessionLocal, engine
import database_model

app = FastAPI()

# create tables
database_model.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def greet():
    return "Hello, welcome to the program!"


products = [
    Product(id=1, name="Hardcover Dotted Notebook",
            description="A5 lay-flat journal with 192 thick pages and an elastic closure.",
            price=10.99, quantity=5),
    Product(id=2, name="Insulated Travel Mug",
            description="16 oz double-walled stainless steel coffee tumbler with leak-proof lid.",
            price=15.99, quantity=3),
    Product(id=5, name="Braided USB-C Cable",
            description="6 ft nylon-braided fast charging and data transfer cord.",
            price=7.99, quantity=10),
    Product(id=6, name="Wireless Ergonomic Mouse",
            description="Rechargeable 2.4GHz optical mouse with adjustable DPI settings.",
            price=29.99, quantity=14),
    Product(id=7, name="Mechanical Gaming Keyboard",
            description="Compact 75% layout with tactile brown switches and white LED backlight.",
            price=74.50, quantity=8),
    Product(id=8, name="Adjustable Laptop Stand",
            description="Foldable aluminum desk riser compatible with 10 to 17-inch laptops.",
            price=24.99, quantity=20),
]


def init_db():
    db = SessionLocal()
    try:
        # only seed if the table is empty
        if db.query(database_model.Product).count() == 0:
            for product in products:
                db.add(database_model.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()

init_db()


@app.get("/products", response_model=list[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(database_model.Product).all()


@app.get("/product/{id}", response_model=Product)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_model.Product).filter(database_model.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/product", response_model=Product)
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_model.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.put("/product/{id}")
def update_product(id: int, updated_product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.name = updated_product.name
    db_product.description = updated_product.description
    db_product.price = updated_product.price
    db_product.quantity = updated_product.quantity
    db.commit()
    return "Product updated"


@app.delete("/product/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return "Product deleted"