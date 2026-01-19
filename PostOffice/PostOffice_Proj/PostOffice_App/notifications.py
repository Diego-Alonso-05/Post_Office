# ==========================================================
#  MONGO: NOTIFICATIONS ONLY
# ==========================================================
from pymongo import MongoClient
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["postoffice"]
notifications_collection = mongo_db["notifications"]

def create_notification(notification_type, recipient_contact, subject, message, status="pending"):
    """Insert a notification document into MongoDB."""
    try:
        notifications_collection.insert_one(
            {
                "notification_type": notification_type,
                "recipient_contact": recipient_contact,
                "subject": subject,
                "message": message,
                "status": status,
                "created_at": timezone.now(),
            }
        )
    except Exception:
        # Avoid breaking core flow if Mongo is down
        pass