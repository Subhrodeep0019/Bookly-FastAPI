from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta

from .schemas import ( UserCreateModel, LoginModel, ResetPassModel,
                       UserDataModel, LoginResponseModel, RefreshResponseModel,
                       UserWithBookAndReviews, UserVerifyResponse )

from .service import UserService
from .utils import (create_token, verify_pass, create_url_safe_token,
                    decode_url_safe_token )
from .dependencies import ( RefreshTokenBearer, AccessTokenBearer,
                            get_curr_user, RoleChecker )

from src.db.main import get_session
from src.db.redis_client import add_to_blocklist
from src.errors import ( UserAlreadyExists, InvalidCredentials,
                         UserNotFound, VerificationError )

from src.config import setting
from src.mail import mail, create_msg
from src.reviews.routes import access_token_bearer
from src.celery_task import send_mail


REFRESH_EXP_DAY = 2 # 2 days

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(['admin', 'user'])

@auth_router.post(
    "/signup",
    response_model=UserVerifyResponse, # removes pass_hash field
    status_code=status.HTTP_201_CREATED,
    summary="Create User Account",
    description="User can create an account by providing required information",
    tags=["user"]
)
async def create_user(
        user_data: UserCreateModel,
        session: AsyncSession = Depends(get_session)
):
    new_user = await user_service.create_user(user_data, session)
    if new_user is not None:
        email = user_data.email
        safe_token = create_url_safe_token({"email": email})
        ver_link = f"http://{setting.DOMAIN}/v1/auth/verify/{safe_token}"
        sub = "Account Verification"
        template_name = "email_verification.html"
        template_body = {
                    "VERIFICATION_LINK": ver_link
        }

        send_mail.delay(
            emails = [email],
            subject = sub,
            temp_body = template_body,
            temp_name = template_name
        )

        return {
            "message": "Account Created! Check email to verify your account",
            "user": new_user
        }
    else:
        raise UserAlreadyExists()



@auth_router.post(
    "/login",
    response_model=LoginResponseModel,
    tags=["user"]
)
async def login_user(
        login_data: LoginModel,
        session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    pswd = login_data.pswd

    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        pass_valid = verify_pass(pwd=pswd, hashed=user.pswd)

        if pass_valid:
            access_token = create_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role
                }
            )

            refresh_token = create_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_EXP_DAY)
            )

            return LoginResponseModel(
                message="Login Successful",
                access_token=access_token,
                refresh_token=refresh_token,
                user= UserDataModel(email=email, user_uid=str(user.uid))
            )
    raise InvalidCredentials()


@auth_router.post(
    "/verify",
    tags=["verification"]
)
async def verify_acc(
        payload: dict = Depends(access_token_bearer)
):
    email = payload.get("user", {}).get("email")

    safe_token = create_url_safe_token({"email": email})
    ver_link = f"http://{setting.DOMAIN}/v1/auth/verify/{safe_token}"
    sub = "Account Verification"
    template_name = "email_verification.html"
    template_body = {
        "VERIFICATION_LINK": ver_link
    }
    send_mail.delay(
        emails = [email],
        subject = sub,
        temp_body = template_body,
        temp_name = template_name
    )

    return {"msg": "email sent. "}


@auth_router.get(
    "/verify/{safe_token}",
    tags=["verification"]
)
async def immediate_verify(
        safe_token: str,
        session: AsyncSession = Depends(get_session)
):
    token_data: dict = decode_url_safe_token(safe_token)
    user_email = token_data.get("email")
    # db query if email exists
    if user_email:
        curr_user = await user_service.get_user_by_email(user_email, session)
        if not curr_user:
            raise UserNotFound()
        await user_service.update_user(
            curr_user,
            {"is_verified": True},
            session
        )
        return JSONResponse(
            content = {"message": "Verification Successful"},
            status_code = status.HTTP_200_OK
        )
    raise VerificationError()


@auth_router.post(
    "/refresh-token",
    response_model=RefreshResponseModel,
    tags=["user"]
)
async def get_new_session(
    session: AsyncSession = Depends(get_session),
    payload = Depends(refresh_token_bearer)
):
    # user_data = {
    #     'email': user.email,
    #     'uid': str(user.uid)
    # }
    user_data = payload["user"]
    # check if user exists
    user = await user_service.get_user_by_email(user_data["email"], session)
    if user is not None:
        new_session_token = create_token(
            user_data
        )
        return RefreshResponseModel(
            access_token=new_session_token,
            user=user_data
        )
    raise UserNotFound()

@auth_router.get(
    "/me",
    response_model=UserWithBookAndReviews,
    tags=["user"]
)
async def get_curr_user(
        curr_user = Depends(get_curr_user),
        _: bool = Depends(role_checker)
):
    return curr_user



# only revokes access token not refresh token
@auth_router.post(
    "/logout",
    tags=["user"]
)
async def logout_user(
    payload: dict = Depends(AccessTokenBearer())
):
    jti = payload.get("jti")
    await add_to_blocklist(jti)
    return JSONResponse(
        content={
            "message": "Logged out Successfully"
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.get(
    "/reset_pass",
    tags=["pass"]
)
async def forgot_password(
        payload = Depends(access_token_bearer)
):
    email = payload.get("user", {}).get("email")

    token = create_url_safe_token({"email": email})

    res_link = f"http://{setting.DOMAIN}/v1/auth/reset_pass/{token}"
    sub = "Reset Password"
    template_body = {
        "RESET_LINK": res_link
    }
    template_name = "password_reset.html"

    send_mail.delay(
        emails=[email],
        subject=sub,
        temp_body=template_body,
        temp_name=template_name
    )

    return {"msg": "email sent. "}


@auth_router.patch(
    "/reset_pass/{token}",
    tags=["pass"]
)
async def reset_password(
        token: str,
        reset_data: ResetPassModel,
        session: AsyncSession = Depends(get_session)
):
    token_data: dict = decode_url_safe_token(token)
    email = token_data.get("email")
    if not email:
        raise InvalidCredentials() # error: InvalidResetToken()

    curr_user = await user_service.get_user_by_email(email, session)
    if not curr_user:
        raise UserNotFound()

    new_pass = reset_data.new_password
    await user_service.reset_pass(new_pass, curr_user, session)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Password reset successful"
        }
    )



