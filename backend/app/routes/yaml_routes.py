"""
API routes for YAML parsing, validation, and explanation.
"""

from fastapi import APIRouter, HTTPException
from ..schemas import (
    YAMLParseRequest, YAMLParseResponse, ParsedResource,
    YAMLValidateRequest, YAMLValidateResponse,
    ExplainRequest, ExplanationResponse, FieldExplanation,
    GenerateRequest
)
from ..services import YAMLService, K8sExplainer, LLMService
from ..database import get_session
from ..models import LLMConnection
from ..services.crypto_service import CryptoService
from sqlalchemy import select

router = APIRouter(prefix="/api/v1", tags=["yaml"])

# Initialize services
yaml_service = YAMLService()
explainer = K8sExplainer()
llm_service = LLMService()
crypto_service = CryptoService()


@router.post("/parse", response_model=YAMLParseResponse)
async def parse_yaml(request: YAMLParseRequest):
    """
    Parse YAML content into structured Kubernetes resources.
    """
    success, documents, error = yaml_service.parse(request.content)
    
    if not success:
        return YAMLParseResponse(success=False, resources=[], error=error)
    
    resources = yaml_service.extract_resources(documents)
    
    parsed_resources = [
        ParsedResource(
            kind=r["kind"],
            api_version=r["api_version"],
            name=r["name"],
            namespace=r["namespace"],
            content=r["content"]
        )
        for r in resources
    ]
    
    return YAMLParseResponse(success=True, resources=parsed_resources)


@router.post("/validate", response_model=YAMLValidateResponse)
async def validate_yaml(request: YAMLValidateRequest):
    """
    Validate YAML against Kubernetes schemas and best practices.
    """
    # First parse the YAML
    success, documents, error = yaml_service.parse(request.content)
    
    if not success:
        return YAMLValidateResponse(
            success=False,
            valid=False,
            issues=[],
            error=error
        )
    
    # Extract resources
    resources = yaml_service.extract_resources(documents)
    
    if not resources:
        return YAMLValidateResponse(
            success=False,
            valid=False,
            issues=[],
            error="No valid Kubernetes resources found"
        )
    
    # Validate structure
    is_valid, issues = yaml_service.validate_structure(resources)
    
    return YAMLValidateResponse(
        success=True,
        valid=is_valid,
        issues=issues
    )


@router.post("/explain", response_model=ExplanationResponse)
async def explain_yaml(request: ExplainRequest):
    """
    Generate explanations for YAML fields using rule-based engine and optionally LLM.
    """
    # Parse YAML
    success, documents, error = yaml_service.parse(request.content)
    
    if not success:
        return ExplanationResponse(
            success=False,
            resources=[],
            explanations=[],
            summary="",
            llm_used=False,
            error=error
        )
    
    # Extract resources
    resources_data = yaml_service.extract_resources(documents)
    
    if not resources_data:
        return ExplanationResponse(
            success=False,
            resources=[],
            explanations=[],
            summary="",
            llm_used=False,
            error="No valid Kubernetes resources found"
        )
    
    # Convert to response format
    parsed_resources = [
        ParsedResource(
            kind=r["kind"],
            api_version=r["api_version"],
            name=r["name"],
            namespace=r["namespace"],
            content=r["content"]
        )
        for r in resources_data
    ]
    
    # Generate rule-based explanations
    all_explanations = []
    for resource in resources_data:
        content = resource["content"]
        explanations = explainer.walk_and_explain(content)
        all_explanations.extend(explanations)
    
    # Generate summary
    summary = explainer.generate_summary(resources_data)
    
    # If LLM is requested, try to get enhanced explanation
    llm_used = False
    if request.use_llm:
        try:
            # Get active LLM connection
            async with get_session() as session:
                result = await session.execute(
                    select(LLMConnection).where(LLMConnection.is_active == True)
                )
                llm_config = result.scalars().first()
                
                if llm_config:
                    # Decrypt API key
                    api_key = crypto_service.decrypt(llm_config.api_key_encrypted)
                    
                    # Get LLM explanation
                    llm_success, llm_explanation, llm_error = await llm_service.explain_with_llm(
                        endpoint=llm_config.endpoint,
                        api_key=api_key,
                        resources=resources_data,
                        rule_explanations=all_explanations,
                        model_name=llm_config.model_name
                    )
                    
                    if llm_success and llm_explanation:
                        # Add LLM summary as a special explanation
                        all_explanations.insert(0, {
                            "path": "_llm_summary",
                            "value": "",
                            "explanation": llm_explanation,
                            "source": "llm"
                        })
                        llm_used = True
                        summary = llm_explanation
        except Exception as e:
            # LLM is optional, continue with rule-based explanations
            print(f"LLM explanation failed: {e}")
    
    # Convert to response format
    field_explanations = [
        FieldExplanation(
            path=exp["path"],
            value=exp["value"],
            explanation=exp["explanation"],
            source=exp["source"]
        )
        for exp in all_explanations
    ]
    
    return ExplanationResponse(
        success=True,
        resources=parsed_resources,
        explanations=field_explanations,
        summary=summary,
        llm_used=llm_used
    )


@router.post("/generate")
async def generate_yaml(request: GenerateRequest):
    """
    Generate YAML manifest for a Kubernetes resource using a wizard.
    """
    success, yaml_content, error = yaml_service.generate_yaml(
        request.resource_type,
        request.config
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "success": True,
        "yaml": yaml_content
    }
