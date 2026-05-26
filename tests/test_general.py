
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
        job_type="remote"
    )
    assert job.title == "Software Engineer"
    assert job.company == "Tech Company"
    assert job.description == "An exciting role in a fast-paced environment."
    assert job.source == "remotive"
    assert job.url == "https://example.com/job/123"
    assert job.location == "Worldwide"
    assert job.country is None
    assert job.job_type == "remote"


def test_keyword_gate_passes_relevant_python_backend_job():
    job = JobListing(
        title="Python Backend Developer",
        company="Tech Company",
        description="We are looking for a Python backend developer with experience in FastAPI.",
        source="remotive",
        url="https://example.com/job/456",
        location="Remote",
        country=None,
        job_type="remote"
    )
    cv_text = "Experienced Python developer with knowledge of FastAPI and backend development."
    preferences = {
        "core_keywords": ["python", "fastapi", "backend"],
        "supporting_keywords": ["django", "sql", "api"],
        "minimum_core_matches": 2,
        "minimum_supporting_matches": 1
    }
    result = score_job(cv_text=cv_text, job=job, preferences=preferences)
    assert result.passed_gate is True
    assert result.keyword_score == 70
    assert set(result.matched_core_keywords) == {"python", "fastapi", "backend"}
    assert set(result.matched_supporting_keywords) == {"api"}

def test_keyword_gate_fails_irrelevant_job():
    cv_text = "Python backend developer with FastAPI and SQL experience."

    preferences = {
        "core_keywords": ["python", "backend", "fastapi", "postgresql"],
        "supporting_keywords": ["sql", "rest api", "docker", "git", "ai", "remote"],
        "minimum_core_matches": 2,
        "minimum_supporting_matches": 1,
    }

    job = JobListing(
        title="Senior Java Engineer",
        company="EnterpriseSoft",
        description="Java, Spring Boot, Kafka, Kubernetes.",
        source="manual_test",
        url="https://example.com/java",
        job_type="onsite",
    )

    result = score_job(cv_text=cv_text, job=job, preferences=preferences)

    assert result.passed_gate is False