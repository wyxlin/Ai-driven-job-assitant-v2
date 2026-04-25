# Job Evaluation Prompt Template

## Step 1 — Context block (paste once at the start of a new conversation)

```
I am a new-grad MS Computer Science student (Arizona State University, graduating 2025)
based in Kirkland, WA, looking for Software Engineer / SWE / Developer roles.

My core skills:
- Languages: Java, Python, SQL
- Backend: gRPC, REST APIs, PostgreSQL, SQLite
- Concepts: distributed systems basics, ORM, data pipelines
- Projects:
  [paste your 3-4 resume project bullets here]

Evaluation criteria (in order of importance):
1. Technical skill overlap — do they need Java/Python/backend work I have done?
2. Seniority fit — I am entry-level; prefer IC individual contributor roles, not management
3. Location — Seattle area or US remote only (already pre-filtered)
```

---

## Step 2 — Per-batch instruction (paste before each CSV chunk)

```
Below is a batch of job listings in CSV format (title, company, location,
date_posted, description, apply_url).

For each job, output one row in this exact CSV format:
  score,title,company,pros,cons,apply_url

Rules:
- score: integer 1–10 (10 = perfect match for a new-grad backend SWE)
- pros: max 1 sentence — what specifically matches my background
- cons: max 1 sentence — the biggest gap or concern
- If score < 5, still include the row so I can see why it was low
- Do not skip any job from the input batch
- Output ONLY the CSV rows, no headers, no extra commentary

--- JOBS START ---
[paste CSV rows here]
--- JOBS END ---
```

---

## Step 3 — Final sort (after all batches are scored)

```
Here are all my scored job rows combined. Please:
1. Sort by score descending
2. Keep only score >= 6
3. Add a header row: score,title,company,pros,cons,apply_url
4. Output the final CSV only, no extra text
```

---

## Usage notes

- Filtered jobs are at: data/filtered_jobs.csv (79 rows as of 2026-04-25)
- Suggested batch size: 10–15 rows at a time
- Paste Step 1 once per conversation, then repeat Step 2 for each batch
- Collect all scored rows, then use Step 3 to get your final ranked list
