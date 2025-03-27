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

## Installation

1. Clone the repository:
    ```bash
    git clone git@github.com:prince-dsd/unicart.git
    cd unicart
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Create a superuser for the admin panel:
    ```bash
    python manage.py createsuperuser
    ```

6. Start the development server:
    ```bash
    python manage.py runserver
    ```

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