from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    total_price = 0
    
    # Start a transaction
    db_transaction = models.Transaction(user_id=user_id, total_price=0) # Temp total_price
    db.add(db_transaction)
    db.flush() # Use flush to get the transaction ID before commit

    products_to_update = []

    for item in transaction.items:
        db_product = get_product(db, item.product_id)
        if not db_product:
            db.rollback()
            raise ValueError(f"Product with id {item.product_id} not found")
        
        if db_product.stock < item.quantity:
            db.rollback()
            raise ValueError(f"Not enough stock for product {db_product.name}")

        item_total_price = db_product.price * item.quantity
        total_price += item_total_price
        
        db_transaction_item = models.TransactionItem(
            transaction_id=db_transaction.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=db_product.price
        )
        db.add(db_transaction_item)

        # Defer stock update to prevent race conditions if needed, but direct update is fine for now
        db_product.stock -= item.quantity
        products_to_update.append(db_product)

    db_transaction.total_price = total_price
    db.add(db_transaction)
    
    try:
        db.commit()
        db.refresh(db_transaction)
    except Exception as e:
        db.rollback()
        raise e
        
    return db_transaction 