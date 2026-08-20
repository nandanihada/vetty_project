from flask import Flask, Response, g, jsonify


class AppError(Exception):
    status_code: int = 500
    error: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        if message is not None:
            self.message = message


class ValidationError(AppError):
    status_code = 400
    error = "VALIDATION_ERROR"
    message = "Bad request."


class AuthenticationError(AppError):
    status_code = 401
    error = "UNAUTHORIZED"
    message = "Authentication required."


class NotFoundError(AppError):
    status_code = 404
    error = "NOT_FOUND"
    message = "Resource not found."


class UpstreamError(AppError):
    status_code = 502
    error = "UPSTREAM_ERROR"
    message = "Upstream service returned an error."


class GatewayTimeoutError(AppError):
    status_code = 504
    error = "GATEWAY_TIMEOUT"
    message = "Upstream service timed out."


def make_error_response(
    error: str, message: str, request_id: str | None, status_code: int
) -> Response:
    response = jsonify({"error": error, "message": message, "request_id": request_id})
    response.status_code = status_code
    return response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response(exc.error, exc.message, request_id, exc.status_code)

    @app.errorhandler(400)
    def handle_400(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response("BAD_REQUEST", "Bad request.", request_id, 400)

    @app.errorhandler(401)
    def handle_401(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response("UNAUTHORIZED", "Unauthorized.", request_id, 401)

    @app.errorhandler(403)
    def handle_403(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response("FORBIDDEN", "Forbidden.", request_id, 403)

    @app.errorhandler(404)
    def handle_404(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response("NOT_FOUND", "Not found.", request_id, 404)

    @app.errorhandler(405)
    def handle_405(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response(
            "METHOD_NOT_ALLOWED", "Method not allowed.", request_id, 405
        )

    @app.errorhandler(422)
    def handle_422(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response(
            "UNPROCESSABLE_ENTITY", "Unprocessable entity.", request_id, 422
        )

    @app.errorhandler(500)
    def handle_500(exc: Exception) -> Response:
        request_id = getattr(g, "request_id", None)
        return make_error_response(
            "INTERNAL_SERVER_ERROR", "Internal server error.", request_id, 500
        )
