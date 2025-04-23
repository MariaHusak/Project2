### Online Bike Store
This is an online bike store application built with Django. 

### Features
- User authentication (registration, login, logout)
- Product listing and detail page
- Order history
- Admin interface for managing products and orders

### Design patterns

1. Builder
- Purpose:
The Builder pattern allows you to create a complex object step by step. In this case, it is different types of bicycles (regular and electric) with different configurations.

- Why it is useful:
Simplifies the creation of objects with different configurations.
Isolating the logic of building an object from its representation.
It is easy to add new types of bicycles without changing the main code (Director).

2. Singleton
- Purpose:
Singleton ensures that a class has only one instance and provides a global access point to it.

- Why it is useful:
Provides a single connection to MongoDB throughout the application.
Efficient use of resources.

3. Factory
- Purpose:
A facade provides a simplified interface to a complex subsystem - here, it is interaction with the user repository, email service, validation logic, and confirmation.

- Why it is useful:
Hides complex implementation under a simple API (register_user, login_user, confirm_user_email).
Makes testing and logic reuse easier.
Improves code readability and maintainability.

### Model-View-Controller (MVC) architecture
The application follows the MVC architecture, which is a variation of the MVC pattern. In this case, the components are:
- Model: Represents the data and business logic of the application. In this case, it includes the Product and Order models.
- View: Represents the presentation layer. In this case, it includes the HTML templates for rendering the user interface.
- Controller: Handles the user interface and user interaction. In this case, it includes the views for displaying products, handling user authentication, and managing orders.

