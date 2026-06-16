from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import UserCreateModel, UserResponseModel, LoginModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import create_token, decode_token, verify_pass
from datetime import timedelta
from fastapi.responses import JSONResponse


REFRESH_EXP_DAY = 2


auth_router = APIRouter()
user_service = UserService()

@auth_router.post(
    "/signup",
    response_model=UserResponseModel, # removes pass_hash field
    status_code=status.HTTP_201_CREATED
)
async def create_user(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    new_user = await user_service.create_user(user_data, session)
    if new_user is not None:
        return new_user
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user already exists with this email"
        )

@auth_router.post(
    "/login"
)
async def login_user(login_data: LoginModel, session: AsyncSession = Depends(get_session)):
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

            return JSONResponse(
                content={
                    "message": "login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": email,
                        "uid": str(user.uid)
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid Email or Password"
    )