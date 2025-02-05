from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile
from dependencies import FriendRepositoryDep
from schemas import UserCreate, RegisterToken, AuthForm, RegisterForm, FriendShip, UserUpdate
from dependencies import AuthServiceDep, UserServiceDep, TwilioServiceDep, UserRepositoryDep 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from db_utils import add_friendship, check_friendship, get_friendship


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/friend")
async def add_friends(data: FriendShip):
    existing = await check_friendship(data.user_1, data.user_2)
    if existing.data:
        return {"message": "Friendship already exists"}
    
    return await add_friendship(data)

@router.delete("/friend")
async def delete_friends(
    data: FriendShip,
    repo: FriendRepositoryDep
):
    friendship = await get_friendship(data.user_1, data.user_2)
    return await repo.delete(friendship["friend_id"])

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
    user_update = UserUpdate(user_id=user_id, imageUri=filepath)

    background_tasks.add_task(service.save_image, png, filepath)
    background_tasks.add_task(repo.update, user_update)

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
    verification_status = await twilio_service.verify_sms(auth_form.phone_number, auth_form.code)
    if verification_status == 'approved':
        register_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        register_token = auth_service.create_access_token(
            data={
                'phone_number': form.phone_number,
                'status': 'verified',
                'temp_token': True
            },
            expires_delta=register_token_expires
        )

        return RegisterToken(
            status='success',
            register_token=register_token,
            token_type='bearer'
        )
 

@router.post("/register")
async def register(
    register_form: RegisterForm, 
    user_create: UserCreate,
    auth_service: AuthServiceDep
): 
    username = register_form.username
    phone_number = register_form.phone_number
    register_token = register_form.register_token

    verified = auth_service.verify_register_token(register_token, phone_number)
    if not verified:
        return {
            "status": "error"
        }
    user_create = UserCreate(
        username=username,  
        phone=phone_number
    )
    created_user = await auth_service.create_user(user_create)



@router.get('/venmo/{username}')
async def get_venmo(username: str):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    
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
        
    finally:
        driver.quit()

