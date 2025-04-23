from abc import ABC, abstractmethod


class Builder(ABC):
    @abstractmethod
    def add_frame(self):
        pass

    @abstractmethod
    def add_wheels(self):
        pass

    @abstractmethod
    def add_motor(self):
        pass

    @abstractmethod
    def get_product(self):
        pass


class RegularBikeBuilder(Builder):
    def __init__(self):
        self.bike = Product(None, None)

    def add_frame(self):
        self.bike.frame = "Steel"
        return self

    def add_wheels(self):
        self.bike.wheels = "Standard"
        return self

    def add_motor(self):
        return self

    def get_product(self):
        return self.bike


class ElectricBikeBuilder(Builder):
    def __init__(self):
        self.bike = Product(None, None)

    def add_frame(self):
        self.bike.frame = "Aluminum"
        return self

    def add_wheels(self):
        self.bike.wheels = "Reinforced"
        return self

    def add_motor(self):
        self.bike.motor = "500W Motor"
        return self

    def get_product(self):
        return self.bike


class Product:
    def __init__(self, frame, wheels, motor=None):
        self.frame = frame
        self.wheels = wheels
        self.motor = motor

    def __str__(self):
        bike_type = "Electric Bike" if self.motor else "Regular Bike"
        message = f"{bike_type} with {self.frame} frame and {self.wheels} wheels."
        self.send_notification(message)
        return message

    @staticmethod
    def send_notification(message):
        print(f"Order confirmed: {message}")


class Director:
    def __init__(self, builder):
        self.builder = builder

    def construct_bike(self):
        return (
            self.builder
            .add_frame()
            .add_wheels()
            .add_motor()
            .get_product()
        )
