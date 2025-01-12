from fastapi import APIRouter, HTTPException
from schemas import UserCreate, RegisterToken, AuthForm, RegisterForm
from dependencies import AuthServiceDep, FriendRepositoryDep, UserServiceDep, TwilioServiceDep 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/friends/{user_id}")
async def get_friends(user_id: int, service: UserServiceDep, repo: FriendRepositoryDep):
    # return await repo.get_by_user(user_id)
    return await service.get_friends(user_id) 


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
