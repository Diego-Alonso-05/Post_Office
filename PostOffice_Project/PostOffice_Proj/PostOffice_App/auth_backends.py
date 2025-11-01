from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from PostOffice_App.views import users  # your MongoDB collection

class MongoBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        mongo_user = users.find_one({"username": username})
        if mongo_user and mongo_user.get("psswd_hash") == password:
            django_user, created = User.objects.get_or_create(username=username)
            return django_user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
