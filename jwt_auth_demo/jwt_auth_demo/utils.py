from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Add extra fields to all DRF error responses
        response.data["status_code"] = response.status_code
        response.data["error"] = True

        # Customize 404 message
        if response.status_code == 404:
            response.data["detail"] = "The requested resource was not found."

    return response
