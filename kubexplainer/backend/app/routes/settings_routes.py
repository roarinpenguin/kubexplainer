"""
API routes for user settings and LLM configuration.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, delete
from typing import List, Dict, Any
import json

from ..schemas import (
    UserSettingRequest, UserSettingResponse,
    LLMConnectionConfig, LLMConnectionResponse,
    LLMTestRequest
)
from ..models import UserSettings, LLMConnection
from ..database import get_session
from ..services import LLMService, CryptoService

router = APIRouter(prefix="/api/v1", tags=["settings"])

llm_service = LLMService()
crypto_service = CryptoService()


# User Settings endpoints
@router.get("/settings", response_model=Dict[str, str])
async def get_all_settings():
    """
    Get all user settings.
    """
    async with get_session() as session:
        result = await session.execute(select(UserSettings))
        settings = result.scalars().all()
        
        return {s.key: s.value for s in settings}


@router.get("/settings/{key}", response_model=UserSettingResponse)
async def get_setting(key: str):
    """
    Get a specific user setting.
    """
    async with get_session() as session:
        result = await session.execute(
            select(UserSettings).where(UserSettings.key == key)
        )
        setting = result.scalars().first()
        
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        return UserSettingResponse(key=setting.key, value=setting.value)


@router.put("/settings")
async def update_setting(request: UserSettingRequest):
    """
    Create or update a user setting.
    """
    async with get_session() as session:
        # Check if setting exists
        result = await session.execute(
            select(UserSettings).where(UserSettings.key == request.key)
        )
        setting = result.scalars().first()
        
        if setting:
            # Update existing
            setting.value = request.value
        else:
            # Create new
            setting = UserSettings(key=request.key, value=request.value)
            session.add(setting)
        
        await session.commit()
        await session.refresh(setting)
        
        return {"success": True, "key": setting.key, "value": setting.value}


@router.delete("/settings/{key}")
async def delete_setting(key: str):
    """
    Delete a user setting.
    """
    async with get_session() as session:
        await session.execute(
            delete(UserSettings).where(UserSettings.key == key)
        )
        await session.commit()
        
        return {"success": True, "message": f"Setting '{key}' deleted"}


# LLM Configuration endpoints
@router.get("/llm/config", response_model=List[LLMConnectionResponse])
async def get_llm_configs():
    """
    Get all LLM connection configurations (without API keys).
    """
    async with get_session() as session:
        result = await session.execute(select(LLMConnection))
        configs = result.scalars().all()
        
        return [
            LLMConnectionResponse(
                id=c.id,
                name=c.name,
                endpoint=c.endpoint,
                model_name=c.model_name,
                is_active=c.is_active,
                created_at=c.created_at
            )
            for c in configs
        ]


@router.get("/llm/config/{config_id}", response_model=LLMConnectionResponse)
async def get_llm_config(config_id: int):
    """
    Get a specific LLM configuration.
    """
    async with get_session() as session:
        result = await session.execute(
            select(LLMConnection).where(LLMConnection.id == config_id)
        )
        config = result.scalars().first()
        
        if not config:
            raise HTTPException(status_code=404, detail="LLM configuration not found")
        
        return LLMConnectionResponse(
            id=config.id,
            name=config.name,
            endpoint=config.endpoint,
            model_name=config.model_name,
            is_active=config.is_active,
            created_at=config.created_at
        )


@router.post("/llm/config")
async def create_llm_config(request: LLMConnectionConfig):
    """
    Create a new LLM connection configuration.
    """
    async with get_session() as session:
        # Check if name already exists
        result = await session.execute(
            select(LLMConnection).where(LLMConnection.name == request.name)
        )
        existing = result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"LLM configuration with name '{request.name}' already exists"
            )
        
        # Encrypt API key
        encrypted_key = crypto_service.encrypt(request.api_key)
        
        # Serialize custom headers
        custom_headers_str = None
        if request.custom_headers:
            custom_headers_str = json.dumps(request.custom_headers)
        
        # If this is set as active, deactivate others
        if request.is_active:
            await session.execute(
                select(LLMConnection).where(LLMConnection.is_active == True)
            )
            active_configs = result.scalars().all()
            for config in active_configs:
                config.is_active = False
        
        # Create new configuration
        new_config = LLMConnection(
            name=request.name,
            endpoint=request.endpoint,
            api_key_encrypted=encrypted_key,
            model_name=request.model_name,
            custom_headers=custom_headers_str,
            is_active=request.is_active
        )
        
        session.add(new_config)
        await session.commit()
        await session.refresh(new_config)
        
        return {
            "success": True,
            "message": "LLM configuration created successfully",
            "id": new_config.id
        }


@router.put("/llm/config/{config_id}")
async def update_llm_config(config_id: int, request: LLMConnectionConfig):
    """
    Update an existing LLM configuration.
    """
    async with get_session() as session:
        result = await session.execute(
            select(LLMConnection).where(LLMConnection.id == config_id)
        )
        config = result.scalars().first()
        
        if not config:
            raise HTTPException(status_code=404, detail="LLM configuration not found")
        
        # Update fields
        config.name = request.name
        config.endpoint = request.endpoint
        config.api_key_encrypted = crypto_service.encrypt(request.api_key)
        config.model_name = request.model_name
        
        if request.custom_headers:
            config.custom_headers = json.dumps(request.custom_headers)
        
        # Handle active status
        if request.is_active and not config.is_active:
            # Deactivate others
            result = await session.execute(
                select(LLMConnection).where(
                    LLMConnection.is_active == True,
                    LLMConnection.id != config_id
                )
            )
            active_configs = result.scalars().all()
            for other_config in active_configs:
                other_config.is_active = False
        
        config.is_active = request.is_active
        
        await session.commit()
        
        return {
            "success": True,
            "message": "LLM configuration updated successfully"
        }


@router.delete("/llm/config/{config_id}")
async def delete_llm_config(config_id: int):
    """
    Delete an LLM configuration.
    """
    async with get_session() as session:
        await session.execute(
            delete(LLMConnection).where(LLMConnection.id == config_id)
        )
        await session.commit()
        
        return {
            "success": True,
            "message": "LLM configuration deleted successfully"
        }


@router.post("/llm/config/{config_id}/activate")
async def activate_llm_config(config_id: int):
    """
    Set a specific LLM configuration as active.
    """
    async with get_session() as session:
        # Get the config to activate
        result = await session.execute(
            select(LLMConnection).where(LLMConnection.id == config_id)
        )
        config = result.scalars().first()
        
        if not config:
            raise HTTPException(status_code=404, detail="LLM configuration not found")
        
        # Deactivate all others
        result = await session.execute(select(LLMConnection))
        all_configs = result.scalars().all()
        for c in all_configs:
            c.is_active = (c.id == config_id)
        
        await session.commit()
        
        return {
            "success": True,
            "message": f"LLM configuration '{config.name}' is now active"
        }


@router.post("/llm/test")
async def test_llm_connection(request: LLMTestRequest):
    """
    Test connection to an LLM endpoint.
    """
    success, message = await llm_service.test_connection(
        endpoint=request.endpoint,
        api_key=request.api_key,
        model_name=request.model_name
    )
    
    return {
        "success": success,
        "message": message
    }
