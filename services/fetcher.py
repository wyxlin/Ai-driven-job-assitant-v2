from __future__ import annotations

from typing import List

# Fixture data simulating Greenhouse / Lever API responses.
# Mix of Seattle-area, Remote, and out-of-area jobs to exercise the filter.
_FIXTURE_JOBS: List[dict] = [
    {
        "external_id": "gh-001",
        "title": "Senior Software Engineer, Backend",
        "company": "Acme Cloud",
        "location": "Seattle, WA",
        "description": (
            "Design and build distributed systems for our cloud platform. "
            "5+ years Python or Go, strong distributed systems fundamentals, "
            "experience with Kubernetes and AWS."
        ),
        "tech_stack": "Python,Go,Kubernetes,AWS,PostgreSQL",
        "date_posted": "2026-04-20",
        "apply_url": "https://acmecloud.example.com/jobs/gh-001",
    },
    {
        "external_id": "gh-002",
        "title": "Machine Learning Engineer",
        "company": "Horizon AI",
        "location": "Bellevue, WA",
        "description": (
            "Build and deploy ML pipelines at scale. "
            "Required: Python, PyTorch or TensorFlow, MLflow, Spark. "
            "PhD or 3+ years industry ML engineering experience."
        ),
        "tech_stack": "Python,PyTorch,TensorFlow,MLflow,Spark",
        "date_posted": "2026-04-21",
        "apply_url": "https://horizonai.example.com/jobs/gh-002",
    },
    {
        "external_id": "gh-003",
        "title": "Staff Software Engineer, Platform",
        "company": "NovaTech",
        "location": "Redmond, WA",
        "description": (
            "Lead platform reliability and developer tooling. "
            "8+ years software engineering, expertise in CI/CD, observability, "
            "and large-scale service meshes."
        ),
        "tech_stack": "Go,Terraform,Prometheus,Grafana,Kubernetes",
        "date_posted": "2026-04-19",
        "apply_url": "https://novatech.example.com/jobs/gh-003",
    },
    {
        "external_id": "lv-001",
        "title": "Senior Full-Stack Engineer",
        "company": "Pixel Labs",
        "location": "Remote",
        "description": (
            "Build product features end-to-end across React frontend and "
            "Node.js / Python backend. 4+ years full-stack experience, "
            "comfortable with GraphQL and PostgreSQL."
        ),
        "tech_stack": "React,TypeScript,Node.js,Python,GraphQL,PostgreSQL",
        "date_posted": "2026-04-22",
        "apply_url": "https://pixellabs.example.com/jobs/lv-001",
    },
    {
        "external_id": "gh-004",
        "title": "Backend Engineer",
        "company": "FinStar",
        "location": "Austin, TX",
        "description": (
            "Develop high-throughput financial data pipelines. "
            "Java or Kotlin, Kafka, strong SQL skills required."
        ),
        "tech_stack": "Java,Kotlin,Kafka,PostgreSQL",
        "date_posted": "2026-04-18",
        "apply_url": "https://finstar.example.com/jobs/gh-004",
    },
    {
        "external_id": "lv-002",
        "title": "Software Engineer II",
        "company": "Metro Systems",
        "location": "New York, NY",
        "description": (
            "Work on core infrastructure for our enterprise SaaS platform. "
            "3+ years Python or Java, AWS, microservices architecture."
        ),
        "tech_stack": "Python,Java,AWS,Docker",
        "date_posted": "2026-04-17",
        "apply_url": "https://metrosystems.example.com/jobs/lv-002",
    },
]


def fetch_jobs() -> List[dict]:
    """Return fixture job records as if fetched from Greenhouse/Lever."""
    return list(_FIXTURE_JOBS)
