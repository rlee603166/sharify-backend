import random
from re import L
import time
from fastapi import HTTPException, status
import httpx
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from jwt import algorithms
from passlib.context import CryptContext
from schemas import UserInDB, User, UserCreate, TokenData, UserBase
from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, repository):
        self.repository = repository
    
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt


    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.REFRESH_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    
    async def get_user(self, username: str) -> Optional[UserInDB]:
        try:
            return await self.repository.get_by_username(username)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise

    
    async def verify_user_credentials(self, username: str, phone_number: str) -> Optional[UserBase]:
        try:
            user = await self.repository.get_by_username(username)
            if not user:
                return None
            if user['phone'] and phone_number != user['phone']:
                return None
            return UserBase(**user)
        
        except Exception as e:
            print(f"Error during verification: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )
                
    async def verify_register_token(self, token: str, phone_number: str) -> Optional[bool]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            payload_number: str = payload.get("phone_number")
            if phone_number != payload_number:
                return False 
            return True
        except jwt.InvalidTokenError:
            return None
            
    async def verify_token(self, token: str) -> Optional[UserInDB]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
            return await self.repository.get_by_username(token_data.username)
        except jwt.InvalidTokenError:
            return None
        
    
    async def verify_refresh_token(self, token: str) -> Optional[UserInDB]:
        try:
            payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
            return await self.repository.get_by_username(token_data.username)
        except jwt.InvalidTokenError:
            return None
        
    
    async def create_user(self, user_data: UserCreate):
        try:
            existing_username = await self.repository.get_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=400, 
                    detail="Username already taken"
                )

            user_dict = user_data.model_dump()
            
            return await self.repository.create(UserCreate(**user_dict))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating user: {str(e)}"
            )
            

class TwilioService(AuthService):
    def __init__(self, repo, account_sid: str, auth_token: str, service_id: str, http_client: httpx.AsyncClient):
        super().__init__(repo)
        self.auth = (account_sid, auth_token)
        self.service_id = service_id
        self.http_client = http_client
        
        
    async def send_sms(self, phone_number: str) -> str:
        try:
            response = await self.http_client.post(
                f"https://verify.twilio.com/v2/Services/{self.service_id}/Verifications",
                auth=self.auth,
                data={
                    "To": f"+1{phone_number}",
                    "Channel": "sms"
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["status"]
        except httpx.HTTPError as e:
            print(f"Twilio API error: {str(e)}")
            print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise


    async def verify_sms(self, phone_number: str, code: str) -> str:
        response = await self.http_client.post(
            f"https://verify.twilio.com/v2/Services/{self.service_id}/VerificationCheck",
            auth=self.auth,
            data={
                "To": f"+1{phone_number}",
                "Code": code
            }
        )
        result = response.json()
        return result["status"]
    
class MockAuthService:
    def __init__(self):
        pass

    async def get_by_username(self, username: str):
        return {
                'phone_number': '13108745772'
        }
    
    async def send_sms(self, phone_number: str):
        return 'pending'


    async def verify_sms(self, phone_number: str, code: str) -> str:
        return 'approved' 

class MockTwilioService:
    def __init__(self):
        self._verification_codes: Dict[str, Dict[str, any]] = {}
        self.TEST_CODE = "123456"  
        self.code_expiry = 300      

    async def send_verification_code(self, phone_number: str) -> bool:
        """Simulate sending a verification code"""
        code = str(random.randint(100000, 999999))
        self._verification_codes[phone_number] = {
            'code': code,
            'timestamp': time.time(),
            'attempts': 0
        }
        
        # Print code for testing purposes
        print(f"📱 Mock SMS sent to {phone_number} with code: {code}")
        return True

    async def verify_sms(self, phone_number: str, code: str) -> str:
        """Verify the code"""
        stored_data = self._verification_codes.get(phone_number)
        
        # For testing: always accept TEST_CODE
        if code == self.TEST_CODE:
            return 'approved'
        
        if not stored_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verification code sent to this number"
            )
            
        # Check if code has expired
        if time.time() - stored_data['timestamp'] > self.code_expiry:
            del self._verification_codes[phone_number]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired"
            )
            
        # Track failed attempts
        if stored_data['attempts'] >= 3:
            del self._verification_codes[phone_number]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many failed attempts. Please request a new code"
            )
            
        if stored_data['code'] != code:
            stored_data['attempts'] += 1
            return 'pending'
            
        # Code is valid
        del self._verification_codes[phone_number]  # Clean up after successful verification
        return 'approved'

    def _cleanup_expired_codes(self):
        """Clean up expired codes"""
        current_time = time.time()
        expired_numbers = [
            phone 
            for phone, data in self._verification_codes.items() 
            if current_time - data['timestamp'] > self.code_expiry
        ]
        for phone in expired_numbers:
            del self._verification_codes[phone]

