from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.profile import Profile
from models.property import Property
from models.nonce import Nonce
from web3 import Web3
from eth_account.messages import encode_defunct
from models import Base

web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
DATABASE_URL = "postgresql://graso_database_user:I88VUodWqyvqK1EQwVRTFZfTaxDc8xix@dpg-crv6rqe8ii6s738mg1h0-a.oregon-postgres.render.com/graso_database"


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Sets up the database connection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# user_id
# id=user_id,
def add_profile(db, **kwargs: dict):
    """Adds a new profile to the database"""
    profile = Profile(**kwargs)
    db.add(profile)
    db.commit()
    return profile

def find_profile(db, id):
    """Finds a profile in the database"""
    return db.query(Profile).filter(Profile.id == id).first()

def add_property(db, **kwargs: dict):
    """Adds a new property to the database"""
    property = Property(**kwargs)
    db.add(property)
    db.commit()
    return property

def get_property(db, id):
    """Finds a property in the database"""
    return db.query(Property).filter(Property.id == id).first()

def get_properties(db):
    """Gets all properties in the database"""
    return db.query(Property).all()

def generate_nonce(wallet_address: str, nonce: str, db):
    """Generates a nonce"""
    save_nonce = db.query(Nonce).filter(Nonce.wallet_address == wallet_address).first()
    if save_nonce:
        print(f"Nonce already exists for wallet: {wallet_address}, Nonce: {save_nonce.nonce}")
        return save_nonce
    save_nonce = Nonce(wallet_address=wallet_address, nonce=nonce)
    print(save_nonce)
    db.add(save_nonce)
    db.commit()
    print(f"Generated and saved nonce for wallet: {wallet_address}, Nonce: {nonce}")
    return save_nonce

def verify(wallet_address: str, nonce: str, signature: str, db):
    """Verifies a signature"""
    wallet_address = web3.to_checksum_address(wallet_address)
    save_nonce = db.query(Nonce).filter(Nonce.wallet_address == wallet_address).first()
    if not save_nonce:
        print("No nonce found for wallet:", wallet_address)
        return False
    if save_nonce.nonce != nonce:
        print("Nonce mismatch. Saved:", save_nonce.nonce, "Received:", nonce)
        return False

    message_hash = encode_defunct(text=nonce)
    recovered_address = web3.eth.account.recover_message(message_hash, signature=signature)

    return web3.to_checksum_address(recovered_address) == web3.to_checksum_address(wallet_address)