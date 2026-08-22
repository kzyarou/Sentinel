from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dependencies import get_db, get_current_user
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
    finding_id: int,
    request: AIAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a finding using AI.
    
    Args:
        finding_id: ID of the finding to analyze
        request: Analysis request options
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        AI analysis response
        
    Raises:
        HTTPException: If analysis fails or user not authorized
    """
    try:
        # Check authorization
        auth_service = AuthorizationService(db)
        if not auth_service.can_user_access_finding(current_user.id, finding_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not authorized to access this finding"
            )
        
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


@router.get("/api/v1/findings/{finding_id}/analysis", response_model=AIAnalysisResponse)
async def get_finding_analysis(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most recent AI analysis for a finding.
    
    Args:
        finding_id: ID of the finding
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        AI analysis response
        
    Raises:
        HTTPException: If analysis not found or user not authorized
    """
    try:
        # Check authorization
        auth_service = AuthorizationService(db)
        if not auth_service.can_user_access_finding(current_user.id, finding_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not authorized to access this finding"
            )
        
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