from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta

from .schemas import ( UserCreateModel, LoginModel,
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
                         UserNotFound )

from ..config import setting
from ..mail import mail, create_msg
from ..reviews.routes import access_token_bearer


REFRESH_EXP_DAY = 2

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(['admin', 'user'])

@auth_router.post(
    "/signup",
    response_model=UserVerifyResponse, # removes pass_hash field
    status_code=status.HTTP_201_CREATED
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

        message = create_msg(
            recipients=[email],
            sub="Account Verification",
            template_body={
                "VERIFICATION_LINK": ver_link
            }
        )

        await mail.send_message(message=message, template_name="email_verification.html")

        return {
            "message": "Account Created! Check email to verify your account",
            "user": new_user
        }
    else:
        raise UserAlreadyExists()



@auth_router.post(
    "/login",
    response_model=LoginResponseModel
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


@auth_router.post("/verify")
async def verify_acc(
        payload: dict = Depends(access_token_bearer)
):
    email = payload.get("user", {}).get("email")

    safe_token = create_url_safe_token({"email": email})
    ver_link = f"http://{setting.DOMAIN}/v1/auth/verify/{safe_token}"

    message = create_msg(
        recipients=[email],
        sub="Account Verification",
        template_body={
            "VERIFICATION_LINK": ver_link
        }
    )

    await mail.send_message(message=message, template_name="email_verification.html")

    return {"msg": "email sent. "}


@auth_router.get("/verify/{safe_token}")
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
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error occurred during verification"
    )


@auth_router.post(
    "/refresh-token",
    response_model=RefreshResponseModel
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
    response_model=UserWithBookAndReviews
)
async def get_curr_user(
        curr_user = Depends(get_curr_user),
        _: bool = Depends(role_checker)
):
    return curr_user



# only revokes access token not refresh token
@auth_router.post(
    "/logout"
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
