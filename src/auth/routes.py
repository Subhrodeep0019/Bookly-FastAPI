from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .schemas import UserCreateModel, UserResponseModel, LoginModel, UserDataModel, LoginResponseModel, RefreshResponseModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import create_token, verify_pass
from datetime import timedelta
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_curr_user
from src.db.redis_client import add_to_blocklist

REFRESH_EXP_DAY = 2


auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()

@auth_router.post(
    "/signup",
    response_model=UserResponseModel, # removes pass_hash field
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        user_data: UserCreateModel,
        session: AsyncSession = Depends(get_session)
):
    new_user = await user_service.create_user(user_data, session)
    if new_user is not None:
        return new_user
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user already exists with this email"
        )



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
                    'user_uid': str(user.uid)
                }
            )

            refresh_token = create_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
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
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid Email or Password"
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
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User doesn't exist"
    )

@auth_router.get(
    "/me",
    response_model=UserResponseModel
)
async def get_curr_user(curr_user = Depends(get_curr_user)):
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
