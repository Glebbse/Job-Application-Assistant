
from app.matcher import score_job
from app.models import JobListing




def test_job_listing_accepts_valid_job():
    job = JobListing(
        title="Software Engineer",
        company="Tech Company",
        description="An exciting role in a fast-paced environment.",
        source="remotive",
        url="https://example.com/job/123",
        location="Worldwide",
        country=None,
        job_type="remote",
        remote_id=123,
        category="Software Development",
        tags=["python", "fastapi", "backend", "AWS", "google cloud"],
        publication_date="2024-01-01",
        salary="$100k-$120k"
    )
    assert job.title == "Software Engineer"
    assert job.company == "Tech Company"
    assert job.description == "An exciting role in a fast-paced environment."
    assert job.source == "remotive"
    assert job.url == "https://example.com/job/123"
    assert job.location == "Worldwide"
    assert job.country is None
    assert job.job_type == "remote"
    assert job.remote_id == 123
    assert job.category == "Software Development"
    assert job.tags == ["python", "fastapi", "backend", "AWS", "google cloud"]
    assert job.publication_date == "2024-01-01"
    assert job.salary == "$100k-$120k"


def test_keyword_gate_passes_relevant_python_backend_job():
    job = JobListing(
        title="Python Backend Developer",
        company="Tech Company",
        description="We are looking for a Python backend developer with experience in FastAPI.",
        source="remotive",
        url="https://example.com/job/456",
        location="Remote",
        country=None,
        job_type="remote",
        remote_id=456,
        category="Software Development",
        tags=["python", "fastapi", "backend"],
        publication_date="2024-01-02",
        salary="$90k-$110k"
    )
    cv_text = "Experienced Python developer with knowledge of FastAPI and backend development."
    preferences = {
        "required_keywords": ["python"],
        "preferred_keywords": ["fastapi", "postgresql", "sqlalchemy", "backend"],
        "supporting_keywords": ["django", "sql", "api"],
        "positive_title_keywords": [
            "junior", 
            "backend", 
            "entry level", 
            "graduate", 
            "intern", 
            "software engineer",
            "software developer",
            "backend developer",
            "python developer"
        ],
        "excluded_description_keywords": ["senior", "manager", "lead"],
        "minimum_preferred_matches": 2,
        "minimum_supporting_matches": 1
    }
    result = score_job(cv_text=cv_text, job=job, preferences=preferences)
    assert result.passed_gate is True
    assert result.keyword_score == 80
    assert set(result.matched_required_keywords) == {"python"}
    assert set(result.matched_preferred_keywords) == {"fastapi", "backend"}
    assert set(result.matched_supporting_keywords) == {"api"}

def test_keyword_gate_fails_irrelevant_job():
    cv_text = "Python backend developer with FastAPI and SQL experience."

    preferences = {
        "required_keywords": ["python"],
        "preferred_keywords": ["fastapi", "postgresql", "sqlalchemy"],
        "supporting_keywords": ["sql", "rest api", "docker", "git", "ai", "remote"],
        "positive_title_keywords": [
            "junior", 
            "backend", 
            "entry level", 
            "graduate", 
            "intern", 
            "software engineer",
            "software developer",
            "backend developer",
            "python developer",
            "python backend developer"
        ],
        "excluded_description_keywords": ["senior", "manager", "lead"],
        "minimum_preferred_matches": 2,
        "minimum_supporting_matches": 1,
    }

    job = JobListing(
        title="Senior Java Engineer",
        company="EnterpriseSoft",
        description="Java, Spring Boot, Kafka, Kubernetes.",
        source="manual_test",
        url="https://example.com/java",
        job_type="onsite",
        remote_id=None,
        category=None,
        tags=["java", "spring", "kafka", "kubernetes"],
        publication_date="2026-01-03",
        salary=None
    )

    result = score_job(cv_text=cv_text, job=job, preferences=preferences)

    assert result.passed_gate is False
    assert result.keyword_score == 0
    assert result.matched_required_keywords == []
    assert result.matched_preferred_keywords == []
    assert result.matched_supporting_keywords == []
    assert result.matched_positive_title_keywords is False
    assert result.rejection_reason == "missing required keyword: python"