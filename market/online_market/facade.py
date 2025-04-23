from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import User


class UserRepository:
    def create_user(self, user_data):
        user_data["password"] = make_password(user_data["password"])
        return User.objects.create(**user_data)

    def get_user_by_email(self, email):
        return User.objects.filter(email=email).first()

    def get_user_by_uid(self, uid):
        return User.objects.get(pk=uid)


class EmailService:
    def send_confirmation_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_url = reverse("confirm_email", kwargs={"uidb64": uid, "token": token})
        full_url = f"http://localhost:8000{confirm_url}"

        subject = "Confirm your registration"
        message = f"Please click the following link to confirm your registration: {full_url}"
        send_mail(subject, message, 'admin@bikeshop.com', [user.email])


class BikeShopFacade:
    def __init__(self):
        self._user_repo = UserRepository()
        self._email_service = EmailService()

    def register_user(self, user_data):
        if not self._validate_user_data(user_data):
            raise ValueError("Invalid user data")
        user = self._user_repo.create_user(user_data)
        self._email_service.send_confirmation_email(user)
        return user

    def login_user(self, email, password):
        user = self._user_repo.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        raise ValueError("Invalid credentials")

    def confirm_user_email(self, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = self._user_repo.get_user_by_uid(uid)
            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                return user
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def _validate_user_data(self, user_data):
        return "email" in user_data and "password" in user_data


