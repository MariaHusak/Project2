from .builder import Director, RegularBikeBuilder, ElectricBikeBuilder
from .models import BikeOrder
from .database import MongoDBConnection


def build_bike(bike_type):
    if bike_type == "electric":
        builder = ElectricBikeBuilder()
    else:
        builder = RegularBikeBuilder()

    director = Director(builder)
    return director.construct_bike()


def create_bike_order(bike_type, bike):
    return BikeOrder.objects.create(
        bike_type=bike_type,
        frame=bike.frame,
        wheels=bike.wheels,
        motor=bike.motor if bike_type == "electric" else None
    )


def log_bike_order(user, bike_type, bike):
    mongo = MongoDBConnection().get_db()
    mongo.bike_orders.insert_one({
        "user": user.username,
        "bike_type": bike_type,
        "frame": bike.frame,
        "wheels": bike.wheels,
        "motor": bike.motor if bike_type == "electric" else None,
    })
