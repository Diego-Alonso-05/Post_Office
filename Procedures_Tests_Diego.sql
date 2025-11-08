import pytest
from datetime import datetime, timezone
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["post_office_db"]

@pytest.fixture(autouse=True)
def clear_collections():
    for col in db.list_collection_names():
        db[col].delete_many({})
    yield


@pytest.mark.mongodb
def test_create_user():
    user = {
        "username": "johndoe",
        "psswd_hash": "hashed123",
        "name": "John Doe",
        "contact": "600111222",
        "address": "Rua Central 10",
        "email": "john@example.com",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "role": "CLIENT"
    }

    result = db.users.insert_one(user)
    assert result.inserted_id is not None
    assert db.users.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_client():
    client_data = {
        "use_id_user": 1,
        "username": "client1",
        "psswd_hash": "hashcli",
        "name": "Client One",
        "contact": "600123456",
        "address": "Rua Verde 23",
        "email": "client@test.com",
        "tax_id": "123456789",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "role": "CLIENT"
    }

    result = db.clients.insert_one(client_data)
    assert result.inserted_id is not None
    assert db.clients.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_post_office_store():
    store = {
        "use_id_user": 1,
        "id_user": 1,
        "name": "Central Store",
        "contact": "700888999",
        "address": "Rua Nova 12",
        "opening_time": "08:00",
        "closing_time": "18:00",
        "po_schedule": "Mon-Fri",
        "maximum_storage": 1000
    }

    result = db.post_office_stores.insert_one(store)
    assert result.inserted_id is not None
    assert db.post_office_stores.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_employee():
    employee = {
        "use_id_user": 1,
        "id_user": 2,
        "id_postoffice_store": 1,
        "username": "emp1",
        "psswd_hash": "hash123",
        "name": "Maria Silva",
        "contact": "622222222",
        "address": "Rua da Luz 40",
        "email": "maria@office.com",
        "role": "EMPLOYEE",
        "position": "Driver",
        "schedule": "Mon-Fri",
        "wage": 1500.0,
        "is_active": True,
        "hire_date": datetime(2024, 5, 1, tzinfo=timezone.utc)
    }

    result = db.employees.insert_one(employee)
    assert result.inserted_id is not None
    assert db.employees.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_invoice():
    invoice = {
        "id_postoffice_store": 1,
        "use_id_user": 1,
        "emp_use_id_user": 1,
        "emp_id_user": 2,
        "id_user": 3,
        "cli_id_user": 4,
        "cost": 50.0,
        "invoice_datetime": datetime(2025, 11, 8, tzinfo=timezone.utc),
        "invoice_status": "PAID"
    }

    result = db.invoices.insert_one(invoice)
    assert result.inserted_id is not None
    assert db.invoices.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_delivery():
    delivery = {
        "use_id_user": 1,
        "id_user": 1,
        "id_invoice": 1,
        "status": "IN_TRANSIT",
        "recipient_address": "Rua Lisboa 45",
        "description": "Fragile package",
        "registered_at": datetime.now(timezone.utc)
    }

    result = db.deliveries.insert_one(delivery)
    assert result.inserted_id is not None
    assert db.deliveries.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_route():
    route = {
        "use_id_user": 1,
        "emp_id_user": 2,
        "id_user": 1,
        "id_delivery": 10,
        "id_postoffice_store": 5,
        "description": "Daily route Lisbon-Porto",
        "delivery_status": "IN_PROGRESS",
        "delivery_date": datetime(2025, 11, 8, tzinfo=timezone.utc),
        "kms_travelled": 312.5,
        "driver_notes": "No issues during trip"
    }

    result = db.routes.insert_one(route)
    assert result.inserted_id is not None
    assert db.routes.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_vehicle():
    vehicle = {
        "id_route": 10,
        "vehicle_type": "Truck",
        "plate_number": "AA-11-BB",
        "capacity": 800.0,
        "brand": "Mercedes",
        "model": "Sprinter",
        "vehicle_status": "AVAILABLE",
        "year": 2022,
        "fuel_type": "Diesel",
        "last_maintenance_date": datetime(2025, 1, 15, tzinfo=timezone.utc)
    }

    result = db.vehicles.insert_one(vehicle)
    assert result.inserted_id is not None
    assert db.vehicles.count_documents({}) == 1


@pytest.mark.mongodb
def test_create_notification():
    notification = {
        "id_delivery": 5,
        "notification_type": "EMAIL",
        "recipient_contact": "client@test.com",
        "subject": "Delivery completed",
        "message": "Your delivery has been successfully completed.",
        "status": "SENT",
        "created_at": datetime.now(timezone.utc)
    }

    result = db.notifications.insert_one(notification)
    assert result.inserted_id is not None
    assert db.notifications.count_documents({}) == 1





