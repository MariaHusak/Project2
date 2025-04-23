from .database import MongoDBConnection
from .facade import BikeShopFacade


def create_user_and_log(form):
    user = form.save(commit=False)
    user.is_verified = False
    user.save()

    mongo = MongoDBConnection().get_db()
    mongo.user_logs.insert_one({
        "email": user.email,
        "action": "registration",
        "is_verified": user.is_verified,
    })

    return user


def confirm_user_email_by_token(uidb64, token):
    facade = BikeShopFacade()
    return facade.confirm_user_email(uidb64, token)


def login_user_via_facade(email, password):
    facade = BikeShopFacade()
    return facade.login_user(email, password)
