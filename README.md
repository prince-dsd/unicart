# Unicart

Unicart is a simple e-commerce platform built using Django. It provides functionalities for managing products, carts, orders, and discount codes. The project is designed to demonstrate the use of Django's ORM, REST framework, and other features for building a scalable web application.

## Features

- User authentication and cart management.
- Add products to the cart and checkout with optional discount codes.
- Admin panel for managing products, orders, and discount codes.
- REST API endpoints for cart and order operations.

## Requirements

- Python 3.8+
- Django 5.1+
- Django REST Framework
- Poetry (for dependency management)

## Installation

1. Clone the repository:
    ```bash
    git clone git@github.com:prince-dsd/unicart.git
    cd unicart
    ```

2. Install Poetry (if not already installed):
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install dependencies using Poetry:
    ```bash
    poetry install
    ```

4. Set up the `.env` file:
    Create a `.env` file in the root directory of the project and add the following keys:
    ```properties
    SECRET_KEY='your-django-secret-key'
    DATABASE_URL='your-database-url'
    ```
    Replace `your-django-secret-key` with a secure key for your Django application, and `your-database-url` with the connection string for your database.

5. Set up the database:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Create a superuser for the admin panel:
    ```bash
    python manage.py createsuperuser
    ```

7. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Running Tests

To run the tests for the application, use the following command:
```bash
python manage.py test
```

This will execute all the test cases defined in the `store/tests/` directory and provide a summary of the results.

## Usage

1. Access the application in your browser at `http://127.0.0.1:8000/`.

2. Use the admin panel at `http://127.0.0.1:8000/admin/` to manage products, orders, and discount codes.

3. Use the API endpoints to interact with the cart and order functionalities:
    - Add items to the cart: `POST /cart/add_item/`
    - Checkout: `POST /cart/checkout/`

## Project Structure

- `store/`: Contains the main application logic, including models, views, serializers, and URLs.
- `unicart/`: Contains project-level settings and configurations.
- `manage.py`: Django's command-line utility for administrative tasks.

## License

This project is licensed under the MIT License.