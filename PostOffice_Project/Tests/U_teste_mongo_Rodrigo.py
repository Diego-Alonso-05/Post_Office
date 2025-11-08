import pytest
from pymongo import MongoClient
from datetime import datetime

# ------------------------------
# Connect to your real MongoDB
# ------------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["postoffice"]

deliveries = db["deliveries"]
notifications = db["notifications"]
postoffice_col = db["postoffice"]
routes = db["routes"]
users = db["users"]
vehicles = db["vehicles"]

# ------------------------------
# Deliveries UPDATE
# ------------------------------
def test_deliveries_update():
    result = deliveries.insert_one({
        "recipient": "Update User",
        "address": "123 Update St",
        "status": "Pending",
        "delivery_date": datetime.now()
    })
    doc_id = result.inserted_id
    print(f"Inserted delivery ID for update: {doc_id}")

    # READ (verify before update)
    doc = deliveries.find_one({"_id": doc_id})
    assert doc is not None
    assert doc["status"] == "Pending"

    # UPDATE
    deliveries.update_one({"_id": doc_id}, {"$set": {"status": "Delivered"}})
    updated_doc = deliveries.find_one({"_id": doc_id})
    assert updated_doc["status"] == "Delivered"
    print("Delivery update verified.")

    # CLEANUP
    deliveries.delete_one({"_id": doc_id})
    assert deliveries.find_one({"_id": doc_id}) is None


# ------------------------------
# Notifications UPDATE
# ------------------------------
def test_notifications_update():
    result = notifications.insert_one({
        "title": "Old Notification",
        "message": "Initial message",
        "date": datetime.now()
    })
    doc_id = result.inserted_id
    print(f"Inserted notification ID for update: {doc_id}")

    doc = notifications.find_one({"_id": doc_id})
    assert doc["title"] == "Old Notification"

    # UPDATE
    notifications.update_one({"_id": doc_id}, {"$set": {"title": "New Notification Title"}})
    updated_doc = notifications.find_one({"_id": doc_id})
    assert updated_doc["title"] == "New Notification Title"
    print("Notification update verified.")

    notifications.delete_one({"_id": doc_id})
    assert notifications.find_one({"_id": doc_id}) is None


# ------------------------------
# Postoffice UPDATE
# ------------------------------
def test_postoffice_update():
    result = postoffice_col.insert_one({
        "name": "Old Postoffice",
        "address": "456 Main St",
        "contact": "555-0000",
        "po_schedule_open": "08:00",
        "po_schedule_close": "17:00",
        "maximum_storage_capacity": 400
    })
    doc_id = result.inserted_id
    print(f"Inserted postoffice ID for update: {doc_id}")

    doc = postoffice_col.find_one({"_id": doc_id})
    assert doc["maximum_storage_capacity"] == 400

    # UPDATE
    postoffice_col.update_one({"_id": doc_id}, {"$set": {"maximum_storage_capacity": 800}})
    updated_doc = postoffice_col.find_one({"_id": doc_id})
    assert updated_doc["maximum_storage_capacity"] == 800
    print("Postoffice update verified.")

    postoffice_col.delete_one({"_id": doc_id})
    assert postoffice_col.find_one({"_id": doc_id}) is None


# ------------------------------
# Routes UPDATE
# ------------------------------
def test_routes_update():
    result = routes.insert_one({
        "route_name": "Route A",
        "origin": "City X",
        "destination": "City Y",
        "distance_km": 100
    })
    doc_id = result.inserted_id
    print(f"Inserted route ID for update: {doc_id}")

    doc = routes.find_one({"_id": doc_id})
    assert doc["distance_km"] == 100

    # UPDATE
    routes.update_one({"_id": doc_id}, {"$set": {"distance_km": 120}})
    updated_doc = routes.find_one({"_id": doc_id})
    assert updated_doc["distance_km"] == 120
    print("Route update verified.")

    routes.delete_one({"_id": doc_id})
    assert routes.find_one({"_id": doc_id}) is None


# ------------------------------
# Users UPDATE
# ------------------------------
def test_users_update():
    result = users.insert_one({
        "username": "user_update",
        "role": "client",
        "email": "updateuser@example.com",
        "password": "old_password"
    })
    doc_id = result.inserted_id
    print(f"Inserted user ID for update: {doc_id}")

    doc = users.find_one({"_id": doc_id})
    assert doc["role"] == "client"

    # UPDATE
    users.update_one({"_id": doc_id}, {"$set": {"role": "admin"}})
    updated_doc = users.find_one({"_id": doc_id})
    assert updated_doc["role"] == "admin"
    print("User update verified.")

    users.delete_one({"_id": doc_id})
    assert users.find_one({"_id": doc_id}) is None


# ------------------------------
# Vehicles UPDATE
# ------------------------------
def test_vehicles_update():
    result = vehicles.insert_one({
        "vehicle_type": "Van",
        "plate_number": "UPD123",
        "capacity": 500,
        "brand": "BrandX",
        "model": "Model1",
        "vehicle_status": "Active",
        "year": 2024,
        "fuel_type": "Diesel",
        "last_maintenance_date": datetime.now()
    })
    doc_id = result.inserted_id
    print(f"Inserted vehicle ID for update: {doc_id}")

    doc = vehicles.find_one({"_id": doc_id})
    assert doc["vehicle_status"] == "Active"

    # UPDATE
    vehicles.update_one({"_id": doc_id}, {"$set": {"vehicle_status": "Inactive"}})
    updated_doc = vehicles.find_one({"_id": doc_id})
    assert updated_doc["vehicle_status"] == "Inactive"
    print("Vehicle update verified.")

    vehicles.delete_one({"_id": doc_id})
    assert vehicles.find_one({"_id": doc_id}) is None
