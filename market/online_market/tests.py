import unittest
from .builder import RegularBikeBuilder, ElectricBikeBuilder, Director
from .facade import BikeShopFacade
from pymongo.errors import ConnectionFailure
from .database import MongoDBConnection
from .user_service import create_user_and_log, confirm_user_email_by_token, login_user_via_facade
from .bike_service import build_bike, create_bike_order, log_bike_order
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import BikeOrder


class TestBikeBuilder(unittest.TestCase):
    def test_creates_regular_bike_with_correct_attributes(self):
        builder = RegularBikeBuilder()
        director = Director(builder)
        bike = director.construct_bike()
        self.assertEqual(bike.frame, "Steel")
        self.assertEqual(bike.wheels, "Standard")
        self.assertIsNone(bike.motor)
        self.assertIn("Regular Bike", str(bike))

    def test_creates_electric_bike_with_correct_attributes(self):
        builder = ElectricBikeBuilder()
        director = Director(builder)
        bike = director.construct_bike()
        self.assertEqual(bike.frame, "Aluminum")
        self.assertEqual(bike.wheels, "Reinforced")
        self.assertEqual(bike.motor, "500W Motor")
        self.assertIn("Electric Bike", str(bike))

    def test_handles_missing_motor_in_regular_bike(self):
        builder = RegularBikeBuilder()
        bike = builder.add_frame().add_wheels().get_product()
        self.assertIsNone(bike.motor)
        self.assertIn("Regular Bike", str(bike))

    def test_handles_missing_wheels_in_bike(self):
        builder = RegularBikeBuilder()
        bike = builder.add_frame().get_product()
        self.assertEqual(bike.frame, "Steel")
        self.assertIsNone(bike.wheels)
        self.assertIn("Regular Bike", str(bike))

    def test_handles_missing_frame_in_bike(self):
        builder = ElectricBikeBuilder()
        bike = builder.add_wheels().add_motor().get_product()
        self.assertIsNone(bike.frame)
        self.assertEqual(bike.wheels, "Reinforced")
        self.assertEqual(bike.motor, "500W Motor")
        self.assertIn("Electric Bike", str(bike))


class TestBikeShopFacade(unittest.TestCase):
    def test_registers_user_with_valid_data(self):
        user_data = {"email": "test@example.com", "password": "securepassword"}
        with patch('online_market.facade.UserRepository.create_user') as mock_create_user, \
             patch('online_market.facade.EmailService.send_confirmation_email') as mock_send_email:
            mock_user = MagicMock()
            mock_create_user.return_value = mock_user
            facade = BikeShopFacade()
            user = facade.register_user(user_data)
            mock_create_user.assert_called_once_with(user_data)
            mock_send_email.assert_called_once_with(mock_user)
            self.assertEqual(user, mock_user)

    def test_raises_error_for_invalid_credentials(self):
        email = "test@example.com"
        password = "wrongpassword"
        with patch('online_market.facade.UserRepository.get_user_by_email', return_value=None):
            facade = BikeShopFacade()
            with self.assertRaises(ValueError) as context:
                facade.login_user(email, password)
            self.assertEqual(str(context.exception), "Invalid credentials")

    def test_logs_in_user_with_correct_credentials(self):
        email = "test@example.com"
        password = "securepassword"
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        with patch('online_market.facade.UserRepository.get_user_by_email', return_value=mock_user):
            facade = BikeShopFacade()
            user = facade.login_user(email, password)
            self.assertEqual(user, mock_user)


class TestMongoDBConnection(unittest.TestCase):

    def setUp(self):
        MongoDBConnection._instance = None

    @patch('online_market.database.MongoClient')
    def test_initializes_connection_with_default_parameters(self, mock_client):
        mock_client.return_value.__getitem__.return_value.name = "bikeshop"
        instance = MongoDBConnection()
        mock_client.assert_called_once_with("mongodb://localhost:27017/")
        self.assertEqual(instance.get_db().name, "bikeshop")

    @patch('online_market.database.MongoClient')
    def test_initializes_connection_with_custom_parameters(self, mock_client):
        mock_client.return_value.__getitem__.return_value.name = "customdb"
        instance = MongoDBConnection(uri="mongodb://customhost:27017/", db_name="customdb")
        mock_client.assert_called_once_with("mongodb://customhost:27017/")
        self.assertEqual(instance.get_db().name, "customdb")

    @patch('online_market.database.MongoClient', side_effect=ConnectionFailure)
    def test_raises_error_on_connection_failure(self, mock_client):
        with self.assertRaises(ConnectionFailure):
            MongoDBConnection()


class TestUserService(unittest.TestCase):
    def test_creates_user_and_logs_registration(self):
        form = MagicMock()
        form.save.return_value = MagicMock(email="test@example.com", is_verified=False)
        with patch('online_market.user_service.MongoDBConnection') as mock_mongo:
            mock_db = mock_mongo.return_value.get_db.return_value
            user = create_user_and_log(form)
            form.save.assert_called_once_with(commit=False)
            mock_db.user_logs.insert_one.assert_called_once_with({
                "email": "test@example.com",
                "action": "registration",
                "is_verified": False,
            })
            self.assertEqual(user.email, "test@example.com")
            self.assertFalse(user.is_verified)

    def test_confirms_user_email_with_valid_token(self):
        with patch('online_market.user_service.BikeShopFacade') as mock_facade:
            mock_facade.return_value.confirm_user_email.return_value = MagicMock(is_verified=True)
            user = confirm_user_email_by_token("valid_uid", "valid_token")
            mock_facade.return_value.confirm_user_email.assert_called_once_with("valid_uid", "valid_token")
            self.assertTrue(user.is_verified)

    def returns_none_for_invalid_email_confirmation(self):
        with patch('online_market.user_service.BikeShopFacade') as mock_facade:
            mock_facade.return_value.confirm_user_email.return_value = None
            user = confirm_user_email_by_token("invalid_uid", "invalid_token")
            mock_facade.return_value.confirm_user_email.assert_called_once_with("invalid_uid", "invalid_token")
            self.assertIsNone(user)

    def test_logs_in_user_with_correct_credentials(self):
        with patch('online_market.user_service.BikeShopFacade') as mock_facade:
            mock_user = MagicMock()
            mock_facade.return_value.login_user.return_value = mock_user
            user = login_user_via_facade("test@example.com", "securepassword")
            mock_facade.return_value.login_user.assert_called_once_with("test@example.com", "securepassword")
            self.assertEqual(user, mock_user)

    def test_raises_error_for_invalid_login_credentials(self):
        with patch('online_market.user_service.BikeShopFacade') as mock_facade:
            mock_facade.return_value.login_user.side_effect = ValueError("Invalid credentials")
            with self.assertRaises(ValueError) as context:
                login_user_via_facade("test@example.com", "wrongpassword")
            mock_facade.return_value.login_user.assert_called_once_with("test@example.com", "wrongpassword")
            self.assertEqual(str(context.exception), "Invalid credentials")


class TestBikeService(unittest.TestCase):
    def test_builds_electric_bike_with_correct_attributes(self):
        with patch('online_market.bike_service.ElectricBikeBuilder') as mock_builder, \
             patch('online_market.bike_service.Director') as mock_director:
            mock_bike = MagicMock(frame="Aluminum", wheels="Reinforced", motor="500W Motor")
            mock_director.return_value.construct_bike.return_value = mock_bike
            bike = build_bike("electric")
            mock_builder.assert_called_once()
            mock_director.assert_called_once_with(mock_builder.return_value)
            self.assertEqual(bike.frame, "Aluminum")
            self.assertEqual(bike.wheels, "Reinforced")
            self.assertEqual(bike.motor, "500W Motor")

    def test_builds_regular_bike_with_correct_attributes(self):
        with patch('online_market.bike_service.RegularBikeBuilder') as mock_builder, \
             patch('online_market.bike_service.Director') as mock_director:
            mock_bike = MagicMock(frame="Steel", wheels="Standard", motor=None)
            mock_director.return_value.construct_bike.return_value = mock_bike
            bike = build_bike("regular")
            mock_builder.assert_called_once()
            mock_director.assert_called_once_with(mock_builder.return_value)
            self.assertEqual(bike.frame, "Steel")
            self.assertEqual(bike.wheels, "Standard")
            self.assertIsNone(bike.motor)

    def test_creates_bike_order_with_correct_data(self):
        with patch('online_market.bike_service.BikeOrder.objects.create') as mock_create:
            bike = MagicMock(frame="Steel", wheels="Standard", motor=None)
            create_bike_order("regular", bike)
            mock_create.assert_called_once_with(
                bike_type="regular",
                frame="Steel",
                wheels="Standard",
                motor=None
            )

    def test_logs_bike_order_to_mongo(self):
        with patch('online_market.bike_service.MongoDBConnection') as mock_mongo:
            mock_db = mock_mongo.return_value.get_db.return_value
            user = MagicMock(username="testuser")
            bike = MagicMock(frame="Steel", wheels="Standard", motor=None)
            log_bike_order(user, "regular", bike)
            mock_db.bike_orders.insert_one.assert_called_once_with({
                "user": "testuser",
                "bike_type": "regular",
                "frame": "Steel",
                "wheels": "Standard",
                "motor": None,
            })


class TestViews(TestCase):
    @patch("online_market.views.build_bike")
    @patch("online_market.views.create_bike_order")
    @patch("online_market.views.log_bike_order")
    def test_builds_and_logs_bike_order_correctly(self, mock_log_order, mock_create_order, mock_build_bike):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="securepassword")
        self.client.force_login(user)

        bike = MagicMock()
        bike.__str__.return_value = "Regular Bike with Steel frame and Standard wheels"
        mock_build_bike.return_value = bike
        order = BikeOrder.objects.create(bike_type="regular", frame="Steel", wheels="Standard", motor=None)
        mock_create_order.return_value = order

        response = self.client.get(reverse("bike") + "?type=regular")

        mock_build_bike.assert_called_once_with("regular")
        mock_create_order.assert_called_once_with("regular", bike)
        mock_log_order.assert_called_once_with(user, "regular", bike)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bike.html")
        self.assertContains(response, "Steel")
        self.assertContains(response, "Standard")

    @patch("online_market.views.confirm_user_email_by_token")
    @patch("online_market.views.create_user_and_log")
    @patch("online_market.views.CustomUserCreationForm")
    def test_creates_user_and_redirects_to_login_on_valid_post_request(self, mock_form_class, mock_create_user, mock_confirm_email):
        mock_form = MagicMock()
        mock_form.is_valid.return_value = True
        mock_form_class.return_value = mock_form

        mock_user = MagicMock()
        mock_create_user.return_value = mock_user

        response = self.client.post("/register/", {})

        mock_create_user.assert_called_once_with(mock_form)
        mock_confirm_email.assert_called_once_with(mock_user)
        self.assertTemplateUsed(response, "login.html")

    def test_renders_login_page_with_error_for_invalid_credentials(self):
        with patch("online_market.views.login_user_via_facade", side_effect=ValueError):
            response = self.client.post("/login/", {"email": "testuser", "password": "wrongpassword"})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "login.html")
            self.assertContains(response, "Невірні облікові дані.")

    def test_renders_login_page_with_error_for_unverified_user(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="securepassword", is_verified=False)
        with patch("online_market.views.login_user_via_facade", return_value=user):
            response = self.client.post("/login/", {"email": "testuser", "password": "securepassword"})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "login.html")
            self.assertContains(response, "Будь ласка, підтвердіть вашу електронну пошту.")


if __name__ == "__main__":
    unittest.main()