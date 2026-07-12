from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.database import get_db
from app.models.user import User
from app.core.security import create_access_token, decode_access_token
from pydantic import BaseModel
from typing import Optional
import httpx
from jose import jwt

router = APIRouter()

CLERK_JWKS_CACHE = {}

async def verify_clerk_token(token: str) -> dict:
    try:
        # Decode header and unverified claims
        unverified_header = jwt.get_unverified_header(token)
        unverified_claims = jwt.get_unverified_claims(token)
        
        kid = unverified_header.get("kid")
        iss = unverified_claims.get("iss")
        
        if not iss:
            raise HTTPException(status_code=401, detail="Invalid token: missing issuer")
            
        jwks_url = f"{iss}/.well-known/jwks.json"
        
        # Check cache
        if jwks_url not in CLERK_JWKS_CACHE:
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                if response.status_code == 200:
                    CLERK_JWKS_CACHE[jwks_url] = response.json()
                else:
                    raise HTTPException(status_code=401, detail="Failed to fetch Clerk JWKS")
                    
        jwks = CLERK_JWKS_CACHE[jwks_url]
        
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwk
                break
                
        if not key:
            raise HTTPException(status_code=401, detail="Signing key not found in JWKS")
            
        # Verify token signature
        decoded = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"JWT verification failed: {str(e)}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class GoogleAuthRequest(BaseModel):
    token: str


class AuthResponse(BaseModel):
    access_token: str
    user: dict


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token"
        )
    
    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate with Google token"""
    from app.core.config import settings
    
    # Check if it's a mock token for demo
    if request.token.startswith("mock_google_token"):
        # Parse email from token if provided in mock_google_token:email format
        parts = request.token.split(":")
        email = parts[1] if len(parts) > 1 else "demo@twinmind.ai"
        
        # Determine name from email
        name = email.split("@")[0].replace(".", " ").title()
        google_id = f"demo_user_{email}"
        picture = None
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                picture=picture,
                is_onboarded=False,
                onboarding_step=0
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Reset onboarding and delete user data on each login to allow re-onboarding
            user.is_onboarded = False
            user.onboarding_step = 0
            user.digital_dna = None
            
            # Delete memories, goals, habits, and conversations
            from app.models.memory import Memory, Conversation
            from app.models.goals import Goal, Habit
            await db.execute(delete(Memory).where(Memory.user_id == user.id))
            await db.execute(delete(Conversation).where(Conversation.user_id == user.id))
            await db.execute(delete(Goal).where(Goal.user_id == user.id))
            await db.execute(delete(Habit).where(Habit.user_id == user.id))
            
            await db.commit()
            await db.refresh(user)
        
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return AuthResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "is_onboarded": user.is_onboarded,
                "onboarding_step": user.onboarding_step,
                "preferred_mode": user.preferred_mode,
                "preferred_tone": user.preferred_tone,
                "preferred_language": user.preferred_language
            }
        )
    
    # Verify Google token for real authentication
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}"
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        token_info = response.json()
        
        if token_info.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience"
            )
    
    email = token_info.get("email")
    name = token_info.get("name")
    google_id = token_info.get("sub")
    picture = token_info.get("picture")
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            email=email,
            name=name,
            google_id=google_id,
            picture=picture,
            is_onboarded=False,
            onboarding_step=0
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update user info
        user.name = name
        user.picture = picture
        await db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "is_onboarded": user.is_onboarded,
            "onboarding_step": user.onboarding_step
        }
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "is_onboarded": current_user.is_onboarded,
        "onboarding_step": current_user.onboarding_step,
        "preferred_mode": current_user.preferred_mode,
        "preferred_tone": current_user.preferred_tone,
        "preferred_language": current_user.preferred_language
    }


class SettingsUpdateRequest(BaseModel):
    preferred_mode: Optional[str] = None
    preferred_tone: Optional[str] = None
    preferred_language: Optional[str] = None


@router.put("/settings")
async def update_settings(
    request: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user settings"""
    if request.preferred_mode is not None:
        current_user.preferred_mode = request.preferred_mode
    if request.preferred_tone is not None:
        current_user.preferred_tone = request.preferred_tone
    if request.preferred_language is not None:
        current_user.preferred_language = request.preferred_language
        
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "is_onboarded": current_user.is_onboarded,
        "onboarding_step": current_user.onboarding_step,
        "preferred_mode": current_user.preferred_mode,
        "preferred_tone": current_user.preferred_tone,
        "preferred_language": current_user.preferred_language
    }


class ClerkAuthRequest(BaseModel):
    token: str
    email: str
    name: str
    picture: Optional[str] = None


@router.post("/clerk", response_model=AuthResponse)
async def clerk_auth(
    request: ClerkAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate or register user with verified Clerk token"""
    claims = await verify_clerk_token(request.token)
    clerk_id = claims.get("sub")
    
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Token verification succeeded but no user ID found")
        
    result = await db.execute(select(User).where(User.google_id == clerk_id))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=request.email,
            name=request.name,
            google_id=clerk_id,
            picture=request.picture,
            is_onboarded=False,
            onboarding_step=0
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.name = request.name
        if request.picture:
            user.picture = request.picture
        await db.commit()
        await db.refresh(user)
        
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "is_onboarded": user.is_onboarded,
            "onboarding_step": user.onboarding_step,
            "preferred_mode": user.preferred_mode,
            "preferred_tone": user.preferred_tone,
            "preferred_language": user.preferred_language
        }
    )
