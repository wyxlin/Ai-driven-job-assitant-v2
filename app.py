from __future__ import annotations

import argparse
import logging
import sys

from sqlalchemy import create_engine

import config
from core.models import Job, JobEvaluation, Resume, get_session, init_db
from services.engine import FilterEngine
from services.fetcher import ingest_all
from services.vetting import VettingService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)


def cmd_fetch(args: argparse.Namespace) -> None:
    count = ingest_all(args.endpoint)
    print(f"Ingested {count} job(s).")


def cmd_filter(args: argparse.Namespace) -> None:
    FilterEngine().run_filter_pass()
    print("Filter pass complete.")


def cmd_vet(args: argparse.Namespace) -> None:
    count = VettingService().process_batch(args.batch_size)
    print(f"Vetted {count} job(s).")


def cmd_report(args: argparse.Namespace) -> None:
    import csv
    with get_session() as session:
        rows = (
            session.query(Job, JobEvaluation)
            .join(JobEvaluation, Job.id == JobEvaluation.job_id)
            .filter(JobEvaluation.match_score >= args.min_score)
            .order_by(JobEvaluation.match_score.desc())
            .all()
        )
    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "score", "title", "company", "location", "reasoning", "apply_url"])
        for i, (job, ev) in enumerate(rows, 1):
            writer.writerow([i, ev.match_score, job.title, job.company,
                             job.location, ev.reasoning, job.apply_url])
    print(f"Exported {len(rows)} job(s) with score ≥ {args.min_score} → {args.out}")


def cmd_seed_resume(args: argparse.Namespace) -> None:
    import json
    with open(args.file) as f:
        data = json.load(f)
    with get_session() as session:
        session.add(Resume(structured_data=data))
    print(f"Resume seeded from {args.file}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app",
        description="AI-Driven Job Assistant — fetch, filter, and vet job listings.",
    )
    parser.add_argument(
        "--db",
        default=config.DB_URL,
        help="SQLAlchemy database URL (default: DATABASE_URL env var)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch and ingest jobs from source")
    p_fetch.add_argument("--endpoint", default="", help="Greenhouse/Lever API endpoint")
    p_fetch.set_defaults(func=cmd_fetch)

    p_filter = sub.add_parser("filter", help="Run location filter pass on unscreened jobs")
    p_filter.set_defaults(func=cmd_filter)

    p_vet = sub.add_parser("vet", help="Run LLM vetting on filtered jobs")
    p_vet.add_argument(
        "--batch-size",
        type=int,
        default=config.MAX_JOBS_PER_RUN,
        dest="batch_size",
        help=f"Max jobs to vet per run (hard cap: {config.MAX_JOBS_PER_RUN})",
    )
    p_vet.set_defaults(func=cmd_vet)

    p_report = sub.add_parser("report", help="Export scored jobs to CSV")
    p_report.add_argument("--min-score", type=int, default=5, dest="min_score",
                          help="Only include jobs at or above this score (default: 5)")
    p_report.add_argument("--out", default="data/results.csv",
                          help="Output CSV path (default: data/results.csv)")
    p_report.set_defaults(func=cmd_report)

    p_seed = sub.add_parser("seed-resume", help="Insert resume JSON into the Resume table (run once)")
    p_seed.add_argument("--file", default="data/resume.json", help="Path to resume JSON file")
    p_seed.set_defaults(func=cmd_seed_resume)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    engine = create_engine(args.db)
    init_db(engine)
    args.func(args)


if __name__ == "__main__":
    main()
