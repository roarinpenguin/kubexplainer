"""
LLM integration service for enhanced YAML explanations.
"""

import httpx
from typing import Dict, Any, Optional
import json

class LLMService:
    """Service for interacting with remote LLM APIs."""
    
    def __init__(self):
        self.timeout = 30.0
    
    async def test_connection(self, endpoint: str, api_key: str, model_name: Optional[str] = None) -> tuple[bool, str]:
        """
        Test connection to an LLM endpoint.
        
        Args:
            endpoint: API endpoint URL
            api_key: API key for authentication
            model_name: Optional model name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Determine API type based on endpoint
                if "openai.com" in endpoint or "api.openai" in endpoint:
                    return await self._test_openai(client, endpoint, api_key, model_name)
                elif "anthropic.com" in endpoint:
                    return await self._test_anthropic(client, endpoint, api_key, model_name)
                else:
                    # Generic test for custom endpoints (Ollama, etc.)
                    return await self._test_generic(client, endpoint, api_key, model_name)
        
        except httpx.TimeoutException:
            return False, "Connection timeout - endpoint not responding"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    async def _test_openai(self, client: httpx.AsyncClient, endpoint: str, api_key: str, model: Optional[str]) -> tuple[bool, str]:
        """Test OpenAI-compatible endpoint."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = await client.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True, "Connection successful"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid API key"
        else:
            return False, f"Connection failed with status {response.status_code}: {response.text[:100]}"
    
    async def _test_anthropic(self, client: httpx.AsyncClient, endpoint: str, api_key: str, model: Optional[str]) -> tuple[bool, str]:
        """Test Anthropic Claude endpoint."""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or "claude-3-sonnet-20240229",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = await client.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True, "Connection successful"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid API key"
        else:
            return False, f"Connection failed with status {response.status_code}"
    
    async def _test_generic(self, client: httpx.AsyncClient, endpoint: str, api_key: str, model: Optional[str]) -> tuple[bool, str]:
        """Test generic/custom LLM endpoint."""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Try OpenAI-compatible format first
        payload = {
            "model": model or "default",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = await client.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True, "Connection successful"
        else:
            return False, f"Connection failed with status {response.status_code}"
    
    async def explain_with_llm(
        self, 
        endpoint: str, 
        api_key: str, 
        resources: list[Dict[str, Any]], 
        rule_explanations: list[Dict[str, Any]],
        model_name: Optional[str] = None
    ) -> tuple[bool, str, str]:
        """
        Get enhanced explanation from LLM.
        
        Args:
            endpoint: LLM API endpoint
            api_key: API key
            resources: Parsed Kubernetes resources
            rule_explanations: Existing rule-based explanations
            model_name: Optional model name
            
        Returns:
            Tuple of (success, explanation_text, error_message)
        """
        try:
            # Build context for LLM
            context = self._build_llm_context(resources, rule_explanations)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if "openai.com" in endpoint or "api.openai" in endpoint:
                    return await self._explain_openai(client, endpoint, api_key, context, model_name)
                elif "anthropic.com" in endpoint:
                    return await self._explain_anthropic(client, endpoint, api_key, context, model_name)
                else:
                    return await self._explain_generic(client, endpoint, api_key, context, model_name)
        
        except Exception as e:
            return False, "", f"LLM explanation failed: {str(e)}"
    
    def _build_llm_context(self, resources: list[Dict], rule_explanations: list[Dict]) -> str:
        """Build context string for LLM prompt."""
        context_parts = ["I have the following Kubernetes manifest:\n"]
        
        for resource in resources:
            kind = resource.get("kind", "Unknown")
            name = resource.get("name", "unnamed")
            context_parts.append(f"- {kind} named '{name}'")
        
        context_parts.append("\nKey fields and their technical meanings:")
        for exp in rule_explanations[:15]:  # Limit to avoid token overflow
            path = exp.get("path", "")
            explanation = exp.get("explanation", "")
            context_parts.append(f"- {path}: {explanation}")
        
        context_parts.append(
            "\nPlease provide a natural language explanation of this manifest, focusing on:\n"
            "1. What this configuration does in practical terms\n"
            "2. How the resources interact with each other\n"
            "3. What happens when this is deployed to a cluster\n"
            "4. Any best practices or potential issues to be aware of\n"
            "Keep the explanation clear and accessible."
        )
        
        return "\n".join(context_parts)
    
    async def _explain_openai(
        self, 
        client: httpx.AsyncClient, 
        endpoint: str, 
        api_key: str, 
        context: str, 
        model: Optional[str]
    ) -> tuple[bool, str, str]:
        """Get explanation from OpenAI-compatible API."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a Kubernetes expert who explains manifests in clear, practical terms."},
                {"role": "user", "content": context}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = await client.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            explanation = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return True, explanation, ""
        else:
            return False, "", f"LLM request failed: {response.status_code}"
    
    async def _explain_anthropic(
        self, 
        client: httpx.AsyncClient, 
        endpoint: str, 
        api_key: str, 
        context: str, 
        model: Optional[str]
    ) -> tuple[bool, str, str]:
        """Get explanation from Anthropic Claude API."""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": context}]
        }
        
        response = await client.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            explanation = data.get("content", [{}])[0].get("text", "")
            return True, explanation, ""
        else:
            return False, "", f"LLM request failed: {response.status_code}"
    
    async def _explain_generic(
        self, 
        client: httpx.AsyncClient, 
        endpoint: str, 
        api_key: str, 
        context: str, 
        model: Optional[str]
    ) -> tuple[bool, str, str]:
        """Get explanation from generic LLM endpoint."""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        payload = {
            "model": model or "default",
            "messages": [{"role": "user", "content": context}],
            "max_tokens": 1000
        }
        
        response = await client.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Try different response formats
            if "choices" in data:
                explanation = data["choices"][0].get("message", {}).get("content", "")
            elif "content" in data:
                explanation = data["content"]
            elif "response" in data:
                explanation = data["response"]
            else:
                explanation = str(data)
            
            return True, explanation, ""
        else:
            return False, "", f"LLM request failed: {response.status_code}"
