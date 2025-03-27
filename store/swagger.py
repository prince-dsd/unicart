from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Unicart API",
        default_version='v1',
        description="API documentation for Unicart e-commerce platform",
        terms_of_service="https://www.unicart.com/terms/",
        contact=openapi.Contact(email="contact@unicart.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

error_responses = {
    400: openapi.Response(
        description="Bad Request",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    ),
    403: openapi.Response(
        description="Permission Denied",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    ),
    404: openapi.Response(
        description="Not Found",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )
}

cart_add_item = {
    "operation_summary": "Add item to cart",
    "operation_description": "Add a product item to the user's shopping cart with specified quantity",
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['product_id', 'quantity'],
        properties={
            'product_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the product to add'
            ),
            'quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Quantity of the product',
                minimum=1
            ),
        }
    ),
    "responses": {
        200: openapi.Response(
            description="Item added successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'items': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'product': openapi.Schema(type=openapi.TYPE_OBJECT),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        )
                    ),
                    'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER)
                }
            )
        ),
        **error_responses
    }
}

cart_add_items = {
    "operation_summary": "Add multiple items to cart",
    "operation_description": "Add multiple product items to the user's shopping cart with specified quantities.",
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['products'],
        properties={
            'products': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'product_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID of the product to add'
                        ),
                        'quantity': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Quantity of the product',
                            minimum=1
                        ),
                    },
                ),
                description='List of products with their quantities'
            ),
        }
    ),
    "responses": {
        200: openapi.Response(
            description="Items added successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'cart': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'items': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'product': openapi.Schema(type=openapi.TYPE_OBJECT),
                                        'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
                                    }
                                )
                            ),
                            'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        404: openapi.Response(
            description="Product not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
    }
}

cart_checkout = {
    "operation_summary": "Checkout cart",
    "operation_description": "Process checkout for the current cart, optionally applying a discount code",
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'coupon_code': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Optional discount coupon code'
            ),
        }
    ),
    "responses": {
        201: openapi.Response(
            description="Order created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'cart': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'discount_code': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        nullable=True
                    ),
                    'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                }
            )
        ),
        **error_responses
    }
}

generate_discount_code = {
    "operation_summary": "Generate discount code",
    "operation_description": "Generate a new discount code for the nth order (Admin only)",
    "method": "post",  # Changed from GET to POST
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nth_order'],
        properties={
            'nth_order': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Order number for which to generate code',
                minimum=1
            ),
        }
    ),
    "responses": {
        201: openapi.Response(
            description="Discount code generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'coupon_code': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        **error_responses
    },
    "security": [{"Bearer": []}]
}

report = {
    "operation_summary": "Generate sales report",
    "operation_description": "Generate a report of sales statistics and discount usage (Admin only)",
    "responses": {
        200: openapi.Response(
            description="Report generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_items_purchased': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Total number of items purchased'
                    ),
                    'total_purchase_amount': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='Total amount of all purchases'
                    ),
                    'discount_codes_used': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Number of discount codes used'
                    )
                }
            )
        ),
        **error_responses
    },
    "security": [{"Bearer": []}]
}