import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.session import Base
from app.models.user import User, UserRole, UserStatus
from app.models.finding import Finding, FindingStatus
from app.models.detection import Detection
from app.models.evidence import Evidence
from app.models.ai_analysis import AIAnalysis


# Test database configuration
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(test_db: Session) -> User:
    """Create a test user."""
    user = User(
        external_id="test-external-id",
        username="testuser",
        email="test@example.com",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_analyst_user(test_db: Session) -> User:
    """Create a test analyst user."""
    user = User(
        external_id="analyst-external-id",
        username="analyst",
        email="analyst@example.com",
        role=UserRole.ANALYST,
        status=UserStatus.ACTIVE
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_finding(test_db: Session, test_user: User) -> Finding:
    """Create a test finding."""
    finding = Finding(
        id="test-finding-1",
        title="Test Finding",
        description="Test finding description",
        severity="HIGH",
        confidence=85,
        status=FindingStatus.OPEN
    )
    test_db.add(finding)
    test_db.commit()
    test_db.refresh(finding)
    return finding


@pytest.fixture
def test_detection(test_db: Session, test_finding: Finding) -> Detection:
    """Create a test detection."""
    detection = Detection(
        id="test-detection-1",
        rule_name="Test Rule",
        description="Test detection description",
        confidence=90,
        detected_at=None
    )
    test_db.add(detection)
    test_db.commit()
    test_db.refresh(detection)
    
    # Link detection to finding
    test_finding.detections.append(detection)
    test_db.commit()
    
    return detection


@pytest.fixture
def test_evidence(test_db: Session, test_detection: Detection) -> Evidence:
    """Create test evidence."""
    evidence = Evidence(
        id="test-evidence-1",
        evidence_type="authentication",
        description="Test evidence description",
        source="test_source",
        confidence=85
    )
    test_db.add(evidence)
    test_db.commit()
    test_db.refresh(evidence)
    
    # Link evidence to detection
    test_detection.evidence.append(evidence)
    test_db.commit()
    
    return evidence