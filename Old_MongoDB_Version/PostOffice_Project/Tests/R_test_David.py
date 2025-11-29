import pytest
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["post_office_db"]


@pytest.fixture(autouse=True)
def setup_sample_data():
    """Crea algunos datos básicos en Mongo antes de cada test"""
    for col in db.list_collection_names():
        db[col].delete_many({})

    db.users.insert_many([
        {"username": "user1", "psswd_hash": "123", "role": "CLIENT"},
        {"username": "user2", "psswd_hash": "456", "role": "EMPLOYEE"}
    ])

    db.clients.insert_many([
        {"username": "client1", "email": "client1@test.com"},
        {"username": "client2", "email": "client2@test.com"}
    ])

    db.employees.insert_many([
        {"username": "emp1", "position": "Driver"},
        {"username": "emp2", "position": "Manager"}
    ])

    db.vehicles.insert_many([
        {"plate_number": "AA-11-BB", "vehicle_type": "Truck"},
        {"plate_number": "CC-22-DD", "vehicle_type": "Van"}
    ])

    db.routes.insert_many([
        {"description": "North Route", "kms_travelled": 250},
        {"description": "South Route", "kms_travelled": 300}
    ])

    db.deliveries.insert_many([
        {"status": "IN_TRANSIT", "recipient_address": "Rua Verde 23"},
        {"status": "DELIVERED", "recipient_address": "Rua Azul 45"}
    ])

    db.invoices.insert_many([
        {"cost": 50.0, "invoice_status": "PAID"},
        {"cost": 30.0, "invoice_status": "PENDING"}
    ])

    db.stores.insert_many([
        {"name": "Central Store", "maximum_storage": 1000},
        {"name": "Mini Store", "maximum_storage": 200}
    ])

    yield


@pytest.mark.mongodb
def test_get_all_users():
    users = list(db.users.find({}))
    assert len(users) == 2
    assert users[0]["username"] == "user1"


@pytest.mark.mongodb
def test_get_all_clients():
    clients = list(db.clients.find({}))
    assert len(clients) == 2
    assert any(c["email"] == "client1@test.com" for c in clients)


@pytest.mark.mongodb
def test_get_all_employees():
    employees = list(db.employees.find({}))
    assert len(employees) == 2
    assert employees[0]["position"] in ["Driver", "Manager"]


@pytest.mark.mongodb
def test_get_all_vehicles():
    vehicles = list(db.vehicles.find({}))
    assert len(vehicles) == 2
    assert any(v["vehicle_type"] == "Truck" for v in vehicles)


@pytest.mark.mongodb
def test_get_all_routes():
    routes = list(db.routes.find({}))
    assert len(routes) == 2
    assert routes[0]["description"] in ["North Route", "South Route"]


@pytest.mark.mongodb
def test_get_all_deliveries():
    deliveries = list(db.deliveries.find({}))
    assert len(deliveries) == 2
    assert any(d["status"] == "IN_TRANSIT" for d in deliveries)


@pytest.mark.mongodb
def test_get_all_invoices():
    invoices = list(db.invoices.find({}))
    assert len(invoices) == 2
    assert any(i["invoice_status"] == "PAID" for i in invoices)


@pytest.mark.mongodb
def test_get_all_stores():
    stores = list(db.stores.find({}))
    assert len(stores) == 2
    assert any(s["name"] == "Central Store" for s in stores)
