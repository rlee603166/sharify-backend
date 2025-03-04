from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from schemas import UserCreate, CreateFriendShip, AuthForm, RegisterForm, FriendShip, UserUpdate, UpdateFriend
from dependencies import AuthServiceDep, UserServiceDep, TwilioServiceDep, UserRepositoryDep, FriendRepositoryDep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from db_utils import add_friendship, check_friendship, get_friend_requests, get_friendship, delete_user_account
from pydantic import BaseModel
from selenium_manager import initialize_driver, get_driver_lock
from datetime import timedelta
from config import get_settings


settings = get_settings()

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/me")
async def get_me(token: Annotated[str, Depends(oauth2_scheme)], auth_service: AuthServiceDep):
    verified = await auth_service.verify_token(token)
    return verified

@router.delete("/me")
async def delete(
    token: Annotated[str, Depends(oauth2_scheme)], 
    auth_service: AuthServiceDep,
    repo: UserRepositoryDep
):
    verified = await auth_service.verify_token(token)
    if verified:
        return await delete_user_account(verified["user_id"])
        


@router.post("/friend")
async def add_friends(data: FriendShip):
    existing = await check_friendship(data.user_1, data.user_2)
    if existing.data:
        return {"message": "Friendship already exists"}
    
    return await add_friendship(
        CreateFriendShip(
            user_1=data.user_1, 
            user_2=data.user_2, 
            status="pending"
        )
    )

@router.patch("/friend")
async def accept(
    data: UpdateFriend,
    repo: FriendRepositoryDep
):
    friendship = await get_friendship(data.user_1, data.user_2)
    return await repo.update(friendship["friend_id"], data)


@router.delete("/friend")
async def delete_friends(
    data: FriendShip,
    repo: FriendRepositoryDep
):
    friendship = await get_friendship(data.user_1, data.user_2)
    return await repo.delete(friendship["friend_id"])


@router.get("/friend-requests/{user_id}")
async def get_requests(user_id: int):
    try:
        requests = await get_friend_requests(user_id)

        result = [
            {
                "user_id": request["user_id"],
                "username": request["username"],
                "name": request["name"],
                "phone": request["phone"],
                "imageUri": request["imageuri"],  # Ensure consistent key naming
                "friend_id": request["friend_id"]
            }
            for request in requests
        ]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friends/{user_id}")
async def get_friends(user_id: int, service: UserServiceDep):
    return await service.get_friends(user_id) 


@router.get("/search/{query}")
async def get_query(query: str, repo: UserRepositoryDep):
    return await repo.get_by_query(query)


@router.post("/pfp/{user_id}")
async def upload_pfp(
    user_id: int,
    image: UploadFile,
    service: UserServiceDep,
    background_tasks: BackgroundTasks,
    repo: UserRepositoryDep
):
    png = await service.standardize(image)
    filepath = service.create_pfp_filepath()
    user_update = UserUpdate(imageUri=filepath)

    background_tasks.add_task(service.save_image, png, filepath)
    background_tasks.add_task(repo.update, user_id, user_update)

    return { 'filepath': filepath }


@router.patch("/pfp/{user_id}")
async def update(user_id: int, data: UserUpdate, repo: UserRepositoryDep):
    return await repo.update(user_id, data)


@router.post("/registerSMS")
async def sms(
    auth_form: AuthForm,
    auth_service: AuthServiceDep,
    twilio_service: TwilioServiceDep
):
    verification_status = await twilio_service.verify_sms(auth_form.phone, auth_form.code)
    if verification_status == 'approved':
        return { "status": "approved" }
    return { "status": "denied" }
        # register_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # register_token = auth_service.create_access_token(
        #     data={
        #         'phone_number': form.phone_number,
        #         'status': 'verified',
        #         'temp_token': True
        #     },
        #     expires_delta=register_token_expires
        # )
        #
        # return RegisterToken(
        #     status='success',
        #     register_token=register_token,
        #     token_type='bearer'
        # )
 
class SMS(BaseModel):
    phone: str

@router.post("/sms")
async def sendSMS(
    form: SMS, 
    user_service: UserServiceDep,
    twilio_service: TwilioServiceDep
):
    phone = form.phone
    existing = await user_service.get_by_phone(phone)
    if existing:
        return { "status": "user already exists" }
    return { "status": await twilio_service.send_sms(form.phone) }


@router.post("/register")
async def register(
    register_form: RegisterForm, 
    auth_service: AuthServiceDep,
    user_service: UserServiceDep
): 
    name = register_form.name
    username = register_form.username
    phone = register_form.phone

    user_create = UserCreate(
        name=name,
        username=username,  
        phone=phone,
        imageUri=register_form.imageUri if register_form.imageUri else None
    )
    created_user = await user_service.create_user(user_create)
    print(created_user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={'sub': username},
        expires_delta=access_token_expires
    )
        
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth_service.create_refresh_token(
        data={'sub': username},
        expires_delta=refresh_token_expires
    )

    return {
        "user": created_user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": 'bearer'
    }
 

@router.get("/venmo/{username}")
async def get_venmo(username: str):
    driver = initialize_driver()
    driver_lock = get_driver_lock()

    with driver_lock:  # Ensure thread-safe access to the browser
        try:
            driver.get(f"https://account.venmo.com/u/{username}")

            avatar_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    ".MuiAvatar-root"
                ))
            )

            username_element = driver.find_element(By.CLASS_NAME, "profileInfo_username__G9vVA")
            handle_element = driver.find_element(By.CLASS_NAME, "profileInfo_handle__adidN")

            handle = handle_element.text.replace('@', '')

            initials = None
            profile_image = None

            try:
                img_element = avatar_element.find_element(By.CLASS_NAME, "MuiAvatar-img")
                profile_image = img_element.get_attribute("src")
            except NoSuchElementException:
                initials = avatar_element.text

            return {
                "name": username_element.text,
                "handle": handle,
                "profile_image": profile_image,
                "initials": initials
            }

        except TimeoutException:
            raise HTTPException(
                status_code=404,
                detail="Profile not found or page took too long to load"
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching profile: {str(e)}"
            )
