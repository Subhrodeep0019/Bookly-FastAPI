from typing import Any, Callable, Awaitable
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request

class BooklyException(Exception):
    """This is the base class of all Bookly errors"""
    pass

class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """User has provided a Refresh token when Access token required"""
    pass

class RefreshTokenRequired(BooklyException):
    """User has provided an Access token when Refresh token required"""
    pass

class UserAlreadyExists(BooklyException):
    """The provided email already exists in Database"""
    pass

class InvalidCredentials(BooklyException):
    """User has provided wrong Email or Password during Login"""
    pass

class InsufficientPermission(BooklyException):
    """User is not permitted to perform this action"""
    pass

class UserNotFound(BooklyException):
    """User not found"""
    pass

class BookNotFound(BooklyException):
    """Book not found"""
    pass

def create_exception_handler(
        status_code: int,
        initial_details: Any
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def exception_handler(req: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            content=initial_details,
            status_code=status_code
        )
    return exception_handler



def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_details={
                "message": "Token is invalid or expired",
                "resolution": "Please get a new token",
                "error_code": "invalid_token"
            }
        )
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_details={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get a new token",
                "error_code": "token_revoked"
            }
        )
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_details={
                "message": "Please provide a valid access token",
                "resolution": "Get a new access token",
                "error_code": "access_token_required"
            }
        )
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "Please provide a valid refresh token",
                "resolution": "Get a new refresh token",
                "error_code": "refresh_token_required"
            }
        )
    )
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_details={
                "message": "User with this email already exists",
                "error_code": "user_exists"
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_details={
                "message": "Invalid Email or Password",
                "error_code": "invalid_email_or_password"
            }
        )
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "You do not have permission to perform this task",
                "error_code": "insufficient_permission"
            }
        )
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": "Book not found",
                "error_code": "book_not_found"
            }
        )
    )
