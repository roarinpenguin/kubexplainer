from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

# Request/Response schemas
class YAMLParseRequest(BaseModel):
    content: str
    
class YAMLValidateRequest(BaseModel):
    content: str

class ExplainRequest(BaseModel):
    content: str
    use_llm: bool = False

class GenerateRequest(BaseModel):
    resource_type: str = Field(..., description="Type of resource: deployment, service, ingress, configmap")
    config: Dict[str, Any] = Field(..., description="Configuration for the resource")

class LLMConnectionConfig(BaseModel):
    name: str
    endpoint: str
    api_key: str
    model_name: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    is_active: bool = True

class LLMConnectionResponse(BaseModel):
    id: int
    name: str
    endpoint: str
    model_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LLMTestRequest(BaseModel):
    endpoint: str
    api_key: str
    model_name: Optional[str] = None

class UserSettingRequest(BaseModel):
    key: str
    value: str

class UserSettingResponse(BaseModel):
    key: str
    value: str
    
    class Config:
        from_attributes = True

# Response models
class FieldExplanation(BaseModel):
    path: str
    value: Any
    explanation: str
    source: str = "rule-based"  # or "llm"

class ValidationIssue(BaseModel):
    severity: str  # error, warning, info
    path: str
    message: str
    suggestion: Optional[str] = None

class ParsedResource(BaseModel):
    kind: str
    api_version: str
    name: Optional[str]
    namespace: Optional[str]
    content: Dict[str, Any]

class YAMLParseResponse(BaseModel):
    success: bool
    resources: List[ParsedResource]
    error: Optional[str] = None

class YAMLValidateResponse(BaseModel):
    success: bool
    valid: bool
    issues: List[ValidationIssue]
    error: Optional[str] = None

class ExplanationResponse(BaseModel):
    success: bool
    resources: List[ParsedResource]
    explanations: List[FieldExplanation]
    summary: str
    llm_used: bool
    error: Optional[str] = None
