from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.dependencies import get_current_user
from app.core.authorization import AuthorizationService
from app.models.user import User
from app.schemas.ai_analysis import AIAnalysisResponse, AIAnalysisRequest
from app.services.ai_analysis_service import AIAnalysisService
from app.ai.mock_provider import MockAIProvider
from app.ai.provider_interface import AIProviderError

router = APIRouter()

# Initialize AI analysis service with mock provider
# In production, this would be configured with a real provider
ai_provider = MockAIProvider()
ai_analysis_service = AIAnalysisService(ai_provider)


@router.post("/findings/{finding_id}/analysis", response_model=AIAnalysisResponse)
async def analyze_finding(
    finding_id: str,
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a finding using AI.
    
    Args:
        finding_id: ID of the finding to analyze
        request: Analysis request options
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AI analysis response
        
    Raises:
        HTTPException: If analysis fails or user not authorized
    """
    try:
        # Check authorization for AI analysis
        AuthorizationService.require_ai_analysis_permission(current_user)
        
        # Perform AI analysis
        ai_analysis = await ai_analysis_service.analyze_finding(
            db=db,
            finding_id=finding_id,
            force_refresh=request.force_refresh
        )
        
        return AIAnalysisResponse(
            id=ai_analysis.id,
            finding_id=ai_analysis.finding_id,
            provider_name=ai_analysis.provider_name,
            model_name=ai_analysis.model_name,
            model_version=ai_analysis.model_version,
            summary=ai_analysis.summary,
            observed_indicators=ai_analysis.observed_indicators,
            possible_interpretation=ai_analysis.possible_interpretation,
            recommended_investigation_steps=ai_analysis.recommended_investigation_steps,
            confidence_notes=ai_analysis.confidence_notes,
            risk_level=ai_analysis.risk_level,
            urgency=ai_analysis.urgency,
            investigation_priority=ai_analysis.investigation_priority,
            created_at=ai_analysis.created_at,
            metadata=ai_analysis.metadata
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AIProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI analysis failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during analysis: {str(e)}"
        )


@router.get("/findings/{finding_id}/analysis", response_model=AIAnalysisResponse)
async def get_finding_analysis(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent AI analysis for a finding.
    
    Args:
        finding_id: ID of the finding
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AI analysis response
        
    Raises:
        HTTPException: If analysis not found or user not authorized
    """
    try:
        # Check authorization for AI analysis
        AuthorizationService.require_ai_analysis_permission(current_user)
        
        # Get existing analysis
        ai_analysis = ai_analysis_service.get_analysis_for_finding(db, finding_id)
        
        if not ai_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No AI analysis found for this finding"
            )
        
        return AIAnalysisResponse(
            id=ai_analysis.id,
            finding_id=ai_analysis.finding_id,
            provider_name=ai_analysis.provider_name,
            model_name=ai_analysis.model_name,
            model_version=ai_analysis.model_version,
            summary=ai_analysis.summary,
            observed_indicators=ai_analysis.observed_indicators,
            possible_interpretation=ai_analysis.possible_interpretation,
            recommended_investigation_steps=ai_analysis.recommended_investigation_steps,
            confidence_notes=ai_analysis.confidence_notes,
            risk_level=ai_analysis.risk_level,
            urgency=ai_analysis.urgency,
            investigation_priority=ai_analysis.investigation_priority,
            created_at=ai_analysis.created_at,
            metadata=ai_analysis.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving analysis: {str(e)}"
        )


@router.get("/ai-analysis/stats")
async def get_ai_analysis_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis error statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AI analysis error statistics
        
    Raises:
        HTTPException: If user not authorized
    """
    try:
        # Check if user is admin
        AuthorizationService.require_audit_log_permission(current_user)
        
        stats = ai_analysis_service.get_error_stats()
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error retrieving statistics: {str(e)}"
        )