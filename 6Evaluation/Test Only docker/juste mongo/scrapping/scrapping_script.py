from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Paramètres MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "test")
MONGO_REPLICA_SET = os.getenv("MONGO_REPLICA_SET", None)

# Fonction pour se connecter à MongoDB
def get_db():
    """
    Renvoie la connexion à MongoDB pour l'application Flask.
    """
    mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
    if MONGO_REPLICA_SET:
        mongo_uri += f"?replicaSet={MONGO_REPLICA_SET}"
    
    client = MongoClient(mongo_uri)
    db = client[MONGO_DB]
    return db

# Fonction pour ajouter ou mettre à jour un produit
def add_or_update_product(asin, name, price):
    """
    Ajoute ou met à jour un produit dans la base de données MongoDB.
    """
    db = get_db()
    collection = db["product_scrapping_url"]

    result = collection.update_one(
        {"asin": asin},
        {
            "$set": {"name": name},
            "$push": {"price_history": {"price": price, "timestamp": datetime.utcnow()}}
        },
        upsert=True,
    )

    return result.modified_count > 0 or result.upserted_id is not None

# Fonction pour supprimer un produit
def delete_product(asin):
    """
    Supprime un produit de la base de données MongoDB.
    """
    db = get_db()
    collection = db["product_scrapping_url"]

    result = collection.delete_one({"asin": asin})
    return result.deleted_count > 0

# Fonction pour récupérer un ou plusieurs produits
def get_products(asins=None, theme=None):
    """
    Récupère des produits depuis la base de données MongoDB.
    """
    db = get_db()
    collection = db["product_scrapping_url"]
    
    if asins:
        if len(asins) == 1:
            return collection.find_one({"asin": asins[0]}, {"_id": 0})
        return list(collection.find({"asin": {"$in": asins}}, {"_id": 0}))

    if theme:
        theme_collection = db["product_scrapping_theme"]
        return theme_collection.find_one({"theme": theme}, {"_id": 0})

    return list(collection.find({}, {"_id": 0}))
