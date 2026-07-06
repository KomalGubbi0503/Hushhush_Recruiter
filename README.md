### Hushhush_Recruiter

An end-to-end recruitment automation platform that replaces manual sourcing and screening with a data-driven pipeline — from collecting candidate technical profiles off GitHub, to ML-based shortlisting, to LLM-powered coding assessments, all surfaced through a live hiring dashboard.

---

## Overview

Traditional technical hiring relies on manually reviewing resumes and GitHub profiles, then running separate coding rounds before a decision is made. This project automates that entire workflow into a single pipeline:

1. **Sourcing** — Pull real technical activity from candidate GitHub profiles via the GitHub API.
2. **Screening** — Feed that activity into a trained ML model that classifies and ranks candidates, shortlisting the top 10 role-matched profiles based on technical fit.
3. **Assessment** — Automatically generate and evaluate a coding assessment for shortlisted candidates using LLM-based code analysis.
4. **Decision** — Track everything on a hiring dashboard, with real-time score visibility and automated selection/rejection communication.

The goal was to take a recruiter's workflow that normally spans days of manual review and compress it into a single automated pipeline that surfaces only the most relevant candidates, backed by objective, data-driven scoring rather than resume keywords alone.

---

## Pipeline Architecture

```
GitHub_data_fetch.py
    │   (fetches raw candidate GitHub activity data)
    ▼
Cleaning and popular_repo.py
    │   (cleans raw data, filters for popular/relevant repos)
    ▼
heat_map.py                      normalise.py
    │   (generates activity heat map)   │   (normalises cleaned data)
    ▼                                    ▼
splitting_data.py
    │   (splits data into train/test sets)
    ▼
k_means.py
    │   (unsupervised learning — initial candidate clustering)
    ▼
supervised_learning.py
    │   (supervised classification — ranks/shortlists top candidates)
    ▼
supervised_learning_MySQL.py   (optional — saves results into MySQL)
    ▼
AI_emplimentation/  (folder)
    │   (runs the AI coding quiz + hiring dashboard)
    ▼
Final Output: Ranked shortlist + assessment scores on dashboard
```

---

## Key Features

### 1. GitHub-Based Candidate Sourcing
- Integrated the GitHub API to pull candidate technical profiles directly from real activity — commits, repositories, languages used, and contribution patterns — instead of relying on self-reported resume claims.
- Collected and processed 4,000+ raw GitHub activity records, filtering and transforming unstructured, noisy data into clean, structured, analysis-ready inputs.

### 2. ML-Based Screening & Shortlisting
- Built a reproducible ML pipeline with self-developed feature engineering to convert raw GitHub signals into model-ready features, including a normalisation step and an activity heat map for exploratory analysis.
- Used unsupervised learning (K-Means clustering) to first group candidates by activity patterns, followed by supervised classification (Scikit-learn) with PCA for dimensionality reduction, to handle high-dimensional GitHub activity data without overfitting.
- Defined evaluation metrics and analysed model outputs to validate pipeline performance before deployment.
- Results can optionally be persisted to a MySQL database for downstream use by the dashboard.
- Output: an automatically ranked shortlist of the top 10 candidates per role, based on technical fit rather than manual judgment alone.

### 3. Automated Coding Assessment
- Built an automated coding assessment pipeline that generates and evaluates candidate submissions using LLM-based code analysis.
- Replaces manual code review rounds with consistent, automated scoring of code quality, correctness, and approach.

### 4. Real-Time Hiring Dashboard
- Centralised dashboard for recruiters to review shortlisted candidates, track assessment scores, and monitor pipeline status in real time.
- Automated selection/rejection communication triggered directly from dashboard decisions, removing manual follow-up emails from the recruiter's workload.

---

## Tech Stack

| Layer                     | Technology                                  |
|---------------------------|----------------------------------------------|
| Data Collection            | Python, GitHub API                          |
| Data Processing            | Python (Pandas/NumPy-based feature engineering) |
| Machine Learning            | Kmeans, PCA, logistic regression                         |
| Code Assessment Engine      | LLM-based code analysis                    |
| Dashboard                  | Web-based hiring dashboard                  |
| Data Storage                | MySQL                                       |

---

## Why This Approach

Resume keyword matching and manual profile review are slow and inconsistent between reviewers. This pipeline instead scores candidates on **actual technical activity** (real code, real contributions) and **actual coding performance** (a real assessment, evaluated automatically), giving a more objective, repeatable signal for the first pass of technical hiring — while still leaving the final decision to a human reviewer via the dashboard.

---

## Project Status

This project was built as an end-to-end proof of concept for automating the early stages of technical recruitment. Core pipeline stages (GitHub data collection, ML shortlisting, automated code assessment, dashboard) are functional; ongoing work includes expanding the feature set used for candidate scoring and refining the LLM assessment rubric for broader role types.

---

## Getting Started

Run the pipeline in the following order:

```bash
# Clone the repository
git clone <repo-url>
cd <repo-folder>

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (GitHub API token, database credentials, LLM API key)
cp .env.example .env

# 1. Fetch raw candidate GitHub activity data
python GitHub_data_fetch.py

# 2. Clean the fetched data and filter for popular/relevant repos
python "Cleaning and popular_repo.py"

# 3. Generate the activity heat map
python heat_map.py

# 4. Normalise the cleaned data
python normalise.py

# 5. Split data into train/test sets
python splitting_data.py

# 6. Run unsupervised learning (initial clustering)
python k_means.py

# 7. Run supervised learning (final classification and ranking)
python supervised_learning.py

# 8. (Optional) Save results to MySQL
python supervised_learning_MySQL.py

# 9. Run the AI coding quiz + hiring dashboard
cd AI_emplimentation

```

> Note: Steps 3 and 4 (heat map generation and normalisation) can be run independently of each other, but both must be completed before splitting the data in step 5.


---

## Authors

Built by Komal Gubbi Deepak, Meghraj Shivakumar, Kavana, Razi .
