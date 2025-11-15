#!/usr/bin/env python3
"""
Test case for JobSpy filtering functionality.
This provides an offline way to test job filtering without making actual API calls.
"""

import sys
from pathlib import Path
import pytest

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Job, SalaryRange
from targets import (
    matches_role_title,
    matches_job_description,
    matches_location,
    filter_jobs,
)


def create_test_jobs():
    """Create a set of test jobs to validate filtering logic."""
    return [
        # Good matches
        Job(
            title="Software Engineer",
            company="Google",
            location="Austin, TX",
            url="https://example.com/job1",
            source="indeed",
            salary=SalaryRange(min=120000, max=180000),
            description="We are looking for a backend software engineer with experience in Python, AWS, and distributed systems. You will work on our cloud platform infrastructure.",
        ),
        Job(
            title="Backend Engineer",
            company="Amazon",
            location="Remote",
            url="https://example.com/job2",
            source="indeed",
            salary=SalaryRange(min=130000, max=200000),
            description="Join our team to build scalable backend services using Java, microservices architecture, and AWS cloud technologies.",
        ),
        Job(
            title="Platform Engineer",
            company="Microsoft",
            location="United States",
            url="https://example.com/job3",
            source="indeed",
            salary=SalaryRange(min=110000, max=170000),
            description="Work on our distributed platform using Scala, Kubernetes, and cloud infrastructure to support millions of users.",
        ),
        # Should be excluded by title
        Job(
            title="Principal Software Engineer",
            company="Facebook",
            location="Austin, TX",
            url="https://example.com/job4",
            source="indeed",
            salary=SalaryRange(min=200000, max=300000),
            description="Lead technical architecture for our backend systems using Python, AWS, and distributed computing.",
        ),
        Job(
            title="Director of Engineering",
            company="Netflix",
            location="Remote",
            url="https://example.com/job5",
            source="indeed",
            salary=SalaryRange(min=250000, max=400000),
            description="Manage engineering teams building backend services with Java, microservices, and cloud platforms.",
        ),
        # Should be excluded by location
        Job(
            title="Software Engineer",
            company="EuropeanCorp",
            location="London, UK",
            url="https://example.com/job7",
            source="indeed",
            salary=SalaryRange(min=80000, max=120000),
            description="Develop backend systems using Python, AWS, and distributed architecture for our European operations.",
        ),
        # Good match with description keywords
        Job(
            title="Software Developer",
            company="PythonCorp",
            location="Remote",
            url="https://example.com/job8",
            source="indeed",
            salary=SalaryRange(min=90000, max=140000),
            description="Python developer needed for backend services, cloud infrastructure, and distributed systems using AWS.",
        ),
    ]


def test_role_title_filtering():
    """Test role title filtering logic."""
    test_jobs = create_test_jobs()
    include_titles = [
        "Software Engineer",
        "Software Developer",
        "Backend Engineer",
        "Platform Engineer",
    ]
    exclude_titles = ["Principal", "Director", "Intern", "Staff", "Lead"]

    # Expected results: job title -> should match (True/False)
    expected_results = {
        "Software Engineer": True,  # Google - should match
        "Backend Engineer": True,  # Amazon - should match
        "Platform Engineer": True,  # Microsoft - should match
        "Principal Software Engineer": False,  # Facebook - should be excluded
        "Director of Engineering": False,  # Netflix - should be excluded
        "Software Developer": True,  # PythonCorp - should match
    }

    for job in test_jobs:
        actual_result = matches_role_title(job, include_titles, exclude_titles)
        expected_result = expected_results.get(job.title, False)
        assert (
            actual_result == expected_result
        ), f"Role title filtering failed for '{job.title}' at {job.company}. Expected {expected_result}, got {actual_result}"


def test_job_description_filtering():
    """Test job description filtering logic."""
    test_jobs = create_test_jobs()
    include_descriptions = [
        "backend",
        "distributed",
        "platform",
        "scala",
        "python",
        "aws",
        "java",
    ]
    exclude_descriptions = [
        "frontend",
        "mobile",
        "ios",
        "android",
        "react",
        "angular",
        "vue",
    ]

    # Expected results: company -> should match (True/False) based on description content
    expected_results = {
        "Google": True,  # "backend software engineer with Python, AWS, and distributed systems"
        "Amazon": True,  # "backend services using Java, microservices architecture, and AWS"
        "Microsoft": True,  # "distributed platform using Scala, Kubernetes, and cloud infrastructure"
        "Facebook": True,  # "backend systems using Python, AWS, and distributed computing"
        "Netflix": True,  # "backend services with Java, microservices, and cloud platforms"
        "EuropeanCorp": True,  # "backend systems using Python, AWS, and distributed architecture"
        "PythonCorp": True,  # "backend services, cloud infrastructure, and distributed systems using AWS"
    }

    for job in test_jobs:
        actual_result = matches_job_description(
            job, include_descriptions, exclude_descriptions
        )
        expected_result = expected_results.get(job.company, False)
        assert (
            actual_result == expected_result
        ), f"Job description filtering failed for '{job.title}' at {job.company}. Expected {expected_result}, got {actual_result}"


def test_location_filtering():
    """Test location filtering logic."""
    test_jobs = create_test_jobs()
    include_locations = ["Austin", "Remote", "United States"]
    exclude_locations = []

    # Expected results: location -> should match (True/False)
    expected_results = {
        "Austin, TX": True,  # Google, Facebook - should match
        "Remote": True,  # Amazon, Netflix, PythonCorp - should match
        "United States": True,  # Microsoft - should match
        "London, UK": False,  # EuropeanCorp - should be excluded
    }

    for job in test_jobs:
        actual_result = matches_location(job, include_locations, exclude_locations)
        expected_result = expected_results.get(job.location, False)
        assert (
            actual_result == expected_result
        ), f"Location filtering failed for '{job.location}'. Expected {expected_result}, got {actual_result}"


def test_combined_filtering():
    """Test the complete filtering pipeline."""
    test_jobs = create_test_jobs()

    # Simulate rules.yaml structure
    rules = {
        "role_titles": {
            "include_any": [
                "Software Engineer",
                "Software Developer",
                "Backend Engineer",
                "Platform Engineer",
            ],
            "exclude_any": ["Principal", "Director", "Intern", "Staff", "Lead"],
        },
        "job_descriptions": {
            "include_any": [
                "backend",
                "distributed",
                "platform",
                "scala",
                "python",
                "aws",
                "java",
            ],
            "exclude_any": [
                "frontend",
                "mobile",
                "ios",
                "android",
                "react",
                "angular",
                "vue",
            ],
        },
        "locations": {
            "include_any": ["Austin", "Remote", "United States"],
            "exclude_any": [],
        },
    }

    filtered_jobs = filter_jobs(test_jobs, rules)

    # Expected: Only jobs that pass ALL three filters (role title AND description AND location)
    # Should pass: Google (Software Engineer + backend description + Austin),
    #              Amazon (Backend Engineer + backend description + Remote),
    #              Microsoft (Platform Engineer + distributed description + United States),
    #              PythonCorp (Software Developer + backend description + Remote)
    # Should fail: Facebook (Principal title), Netflix (Director title), EuropeanCorp (London location)
    expected_passing_companies = {"Google", "Amazon", "Microsoft", "PythonCorp"}
    expected_failing_companies = {"Facebook", "Netflix", "EuropeanCorp"}

    # Check that we got the expected number of results
    assert (
        len(filtered_jobs) == 4
    ), f"Expected 4 filtered jobs, got {len(filtered_jobs)}"

    # Check that the right companies passed
    passing_companies = {job.company for job in filtered_jobs}
    assert (
        passing_companies == expected_passing_companies
    ), f"Expected companies {expected_passing_companies}, got {passing_companies}"

    # Verify no excluded companies made it through
    for job in filtered_jobs:
        assert (
            job.company not in expected_failing_companies
        ), f"Excluded company {job.company} should not have passed filtering"


def test_jobspy_parsing_simulation():
    """Simulate JobSpy parsing to test data structure."""
    try:
        # Simulate what JobSpy might return
        import pandas as pd

        jobspy_data = {
            "title": [
                "Software Engineer",
                "Senior Software Engineer",
                "Principal Software Engineer",
                "Backend Developer",
                "Frontend Developer",
            ],
            "company": ["Google", "Amazon", "Microsoft", "StartupCorp", "FrontendCorp"],
            "location": [
                "Austin, TX",
                "Remote",
                "Seattle, WA",
                "Austin, TX",
                "San Francisco, CA",
            ],
            "job_url": [
                "https://example.com/job1",
                "https://example.com/job2",
                "https://example.com/job3",
                "https://example.com/job4",
                "https://example.com/job5",
            ],
            "salary_min": [120000, 150000, 200000, 80000, 100000],
            "salary_max": [180000, 220000, 300000, 120000, 150000],
            "salary_currency": ["USD", "USD", "USD", "USD", "USD"],
            "salary_period": ["year", "year", "year", "year", "year"],
            "description": [
                "Backend software engineer with Python, AWS, and distributed systems experience.",
                "Senior backend engineer working with Java, microservices, and cloud technologies.",
                "Principal engineer leading technical architecture for distributed systems.",
                "Backend developer building scalable services using Python and cloud infrastructure.",
                "Frontend developer creating user interfaces with React, Angular, and Vue.js.",
            ],
        }

        df = pd.DataFrame(jobspy_data)

        # Test conversion to our Job objects
        from providers.jobspy_search import _df_to_jobs

        jobs = _df_to_jobs(df, "indeed")

        # Assertions for JobSpy parsing
        assert len(jobs) == 5, f"Expected 5 jobs, got {len(jobs)}"

        # Check that all expected fields are populated
        for job in jobs:
            assert job.title, f"Job title should not be empty: {job.title}"
            assert job.company, f"Job company should not be empty: {job.company}"
            assert job.location, f"Job location should not be empty: {job.location}"
            assert job.url, f"Job URL should not be empty: {job.url}"
            assert (
                job.source == "indeed"
            ), f"Job source should be 'indeed', got {job.source}"
            assert (
                job.description
            ), f"Job description should not be empty: {job.description}"
            assert (
                job.salary.min is not None
            ), f"Job salary min should not be None: {job.salary.min}"
            assert (
                job.salary.max is not None
            ), f"Job salary max should not be None: {job.salary.max}"

        # Check specific job data
        google_job = next(job for job in jobs if job.company == "Google")
        assert google_job.title == "Software Engineer"
        assert google_job.location == "Austin, TX"
        assert google_job.salary.min == 120000
        assert google_job.salary.max == 180000
        assert "backend" in google_job.description.lower()

        frontend_job = next(job for job in jobs if job.company == "FrontendCorp")
        assert frontend_job.title == "Frontend Developer"
        assert "react" in frontend_job.description.lower()

    except ImportError:
        pytest.skip("Pandas not available - skipping JobSpy DataFrame simulation")


# Tests can be run with: pytest tests/test_jobspy_filtering.py
# Or run specific test: pytest tests/test_jobspy_filtering.py::test_role_title_filtering
