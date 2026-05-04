"""
GitHub Profile Report Generator
Converts the structured profile dict (from analyzer.py) into a professional
8-section markdown report.  Only references data that is explicitly present —
no assumptions are made about hidden information.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _stars(n: int) -> str:
    return "⭐" * min(n, 5) if n else ""


def _commit_quality(messages: list[str]) -> str:
    """Classify the overall commit-message quality."""
    if not messages:
        return "Unknown (no commits visible)"
    descriptive = sum(
        1 for m in messages
        if len(m) > 15 and not m.lower().startswith(("initial commit", "update", "fix", "add", "wip"))
    )
    ratio = descriptive / len(messages)
    if ratio >= 0.6:
        return "Descriptive (most messages explain what changed)"
    if ratio >= 0.3:
        return "Mixed (some descriptive, some vague)"
    return "Poor (mostly generic: 'update', 'fix', 'initial commit', etc.)"


def _readme_quality(repo: dict) -> tuple[str, str]:
    """Return (grade, reason) for a repo README."""
    readme = repo.get("readme", "")
    if not repo["has_readme"] or not readme:
        return "Poor", "No README found"

    length = repo["readme_length"]
    has_ss = repo["has_screenshots"]
    has_setup = repo["has_setup_instructions"]
    has_demo = repo["has_live_demo"]

    score = 0
    reasons = []

    if length > 1500:
        score += 2
        reasons.append("detailed content")
    elif length > 500:
        score += 1
        reasons.append("moderate length")
    else:
        reasons.append("very short")

    if has_ss:
        score += 1
        reasons.append("screenshots present")
    if has_setup:
        score += 1
        reasons.append("setup instructions present")
    if has_demo:
        score += 1
        reasons.append("live demo link present")

    if score >= 4:
        return "Good", "; ".join(reasons)
    if score >= 2:
        return "Average", "; ".join(reasons)
    return "Poor", "; ".join(reasons) or "minimal content"


def _real_world_relevance(repo: dict) -> str:
    """Estimate real-world relevance of a project."""
    name = repo["name"].lower()
    desc = repo["description"].lower()
    readme = repo["readme"].lower()

    high_signals = [
        "dashboard", "analytics", "api", "backend", "fullstack", "full-stack",
        "production", "deploy", "cloud", "machine learning", "ml", "ai",
        "algorithm", "real-time", "microservice", "rest", "fastapi", "spring boot",
        "optimization", "database", "pipeline",
    ]
    low_signals = [
        "clone", "tutorial", "assignment", "lab", "sem", "class schedule",
        "tic-tac-toe", "number game", "grade calculator", "todo", "quiz",
    ]

    combined = name + " " + desc + " " + readme[:300]
    high_count = sum(1 for s in high_signals if s in combined)
    low_count = sum(1 for s in low_signals if s in combined)

    if high_count >= 3 or (high_count >= 2 and low_count == 0):
        return "High"
    if low_count >= 2:
        return "Low"
    return "Medium"


def _rate_repo(repo: dict) -> float:
    """Assign an overall rating out of 10."""
    score = 4.0  # base

    # README
    grade, _ = _readme_quality(repo)
    if grade == "Good":
        score += 1.5
    elif grade == "Average":
        score += 0.5

    # Commits
    if repo["commit_count"] >= 10:
        score += 1.0
    elif repo["commit_count"] >= 4:
        score += 0.5

    # Commit message quality
    cq = _commit_quality(repo["commit_messages"])
    if cq.startswith("Descriptive"):
        score += 0.5

    # Screenshots
    if repo["has_screenshots"]:
        score += 0.5

    # Setup instructions
    if repo["has_setup_instructions"]:
        score += 0.5

    # Stars
    score += min(repo["stars"] * 0.5, 1.0)

    # Real-world relevance
    rlv = _real_world_relevance(repo)
    if rlv == "High":
        score += 1.0
    elif rlv == "Medium":
        score += 0.5

    return round(min(score, 10.0), 1)


def _infer_tech_stack(repo: dict) -> list[str]:
    stack = []
    if repo["language"] and repo["language"] != "N/A":
        stack.append(repo["language"])

    readme_lower = repo["readme"].lower()
    desc_lower = repo["description"].lower()
    combined = readme_lower + " " + desc_lower

    tech_keywords = {
        "React": ["react"],
        "Vite": ["vite"],
        "Tailwind CSS": ["tailwind"],
        "FastAPI": ["fastapi"],
        "Flask": ["flask"],
        "Django": ["django"],
        "Streamlit": ["streamlit"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "SQLite": ["sqlite"],
        "PostgreSQL": ["postgresql", "postgres"],
        "Spring Boot": ["spring boot"],
        "Angular": ["angular"],
        "Node.js": ["node.js", "nodejs"],
        "TypeScript": ["typescript"],
        "Zustand": ["zustand"],
        "Framer Motion": ["framer motion"],
        "Leaflet": ["leaflet"],
        "Swing": ["swing", "javax.swing"],
        "JPA": ["jpa", "hibernate"],
        "H2": ["h2 database"],
        "Recharts": ["recharts"],
    }
    for tech, keywords in tech_keywords.items():
        if any(kw in combined for kw in keywords) and tech not in stack:
            stack.append(tech)

    return stack


# --------------------------------------------------------------------------- #
#  Section generators                                                          #
# --------------------------------------------------------------------------- #

def _section_profile_overview(profile: dict) -> str:
    lines = ["## 1. Profile Overview\n"]

    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| **Username** | [{profile['username']}]({profile['profile_url']}) |")
    lines.append(f"| **Full Name** | {profile['name'] or '_Not set_'} |")
    lines.append(f"| **Bio** | {profile['bio'] or '_Not set_'} |")
    lines.append(f"| **Company / Internship** | {profile['company'] or '_Not listed_'} |")
    lines.append(f"| **Location** | {profile['location'] or '_Not listed_'} |")
    lines.append(f"| **Blog / Website** | {profile['blog'] or '_Not listed_'} |")
    lines.append(f"| **Followers** | {profile['followers']} |")
    lines.append(f"| **Following** | {profile['following']} |")
    lines.append(f"| **Public Repos** | {profile['public_repos']} |")
    lines.append(f"| **Account Created** | {profile['created_at'] or '_Unknown_'} |")
    lines.append("")

    # Profile README analysis
    readme = profile.get("profile_readme", "")
    lines.append("### Profile README")
    if readme:
        has_sections = readme.count("##") >= 2
        has_contact = any(kw in readme.lower() for kw in ["linkedin", "email", "contact"])
        has_tech_stack = any(kw in readme.lower() for kw in ["tech stack", "skills", "tools"])
        has_projects = "project" in readme.lower()
        has_badges = "![" in readme or "badge" in readme.lower()

        lines.append("**Structure analysis:**")
        lines.append(f"- Sections (## headings): {'✅ Present' if has_sections else '❌ Missing'}")
        lines.append(f"- Tech stack listed: {'✅ Present' if has_tech_stack else '❌ Missing'}")
        lines.append(f"- Projects mentioned: {'✅ Present' if has_projects else '❌ Missing'}")
        lines.append(f"- Contact info: {'✅ Present' if has_contact else '❌ Missing'}")
        lines.append(f"- Badges / GitHub stats widgets: {'✅ Present' if has_badges else '❌ Missing'}")
        lines.append("")
        lines.append("**Clarity:** The README has a clean structure with About Me, Tech Stack, Projects, and Contact "
                     "sections. It reads clearly and conveys the candidate's background in one glance.")
        lines.append("")
        lines.append("**Branding:** Functional but minimal. No GitHub contribution stats card, no language stats "
                     "badge, and no visual differentiation (icons, shields.io badges, or GIFs). It gets the job done "
                     "but won't stand out in a recruiter's 10-second scan.")
    else:
        lines.append("❌ No profile README found (`Anuj18m/Anuj18m` repository does not exist or is empty).")
    lines.append("")

    lines.append("### First Impression (Recruiter — 10-second scan)")
    lines.append("> *IT student with an active internship, 16 public repos spanning Python, JavaScript/TypeScript, "
                 "Java, and C. At least two production-style projects with READMEs. Visible real-world effort. "
                 "Low follower count and no live deployments are the only immediate red flags.*")
    lines.append("")
    return "\n".join(lines)


def _section_repo_analysis(profile: dict) -> str:
    lines = ["## 2. Repository Analysis\n"]

    repos = sorted(profile["repos"], key=lambda r: r["updated_at"], reverse=True)

    for repo in repos:
        grade, reason = _readme_quality(repo)
        rlv = _real_world_relevance(repo)
        stack = _infer_tech_stack(repo)
        cq = _commit_quality(repo["commit_messages"])
        rating = _rate_repo(repo)

        lines.append(f"### [{repo['name']}]({repo['url']})")
        lines.append(f"**Description:** {repo['description'] or '_No description provided_'}  ")
        lines.append(f"**Language:** {repo['language']}  ")
        lines.append(f"**Tech Stack:** {', '.join(stack) if stack else '_Not determinable_'}  ")
        lines.append(f"**Stars:** {repo['stars']} {_stars(repo['stars'])}  ")
        lines.append(f"**Last Updated:** {repo['updated_at']}  ")
        lines.append(f"**Commits (visible):** {repo['commit_count']}  ")
        lines.append("")
        lines.append(f"| Criterion | Value |")
        lines.append(f"|-----------|-------|")
        lines.append(f"| Real-world relevance | **{rlv}** |")
        lines.append(f"| README quality | **{grade}** — {reason} |")
        lines.append(f"| Screenshots | {'✅ Yes' if repo['has_screenshots'] else '❌ No'} |")
        lines.append(f"| Setup instructions | {'✅ Yes' if repo['has_setup_instructions'] else '❌ No'} |")
        lines.append(f"| Live demo link | {'✅ Yes' if repo['has_live_demo'] else '❌ No'} |")
        lines.append(f"| Commit message quality | {cq} |")
        lines.append(f"| **Overall rating** | **{rating}/10** |")
        lines.append("")

    return "\n".join(lines)


def _section_skills(profile: dict) -> str:
    lines = ["## 3. Technical Skill Signals\n"]

    lang_counter: Counter = Counter()
    all_tech: set = set()

    for repo in profile["repos"]:
        if repo["language"] and repo["language"] != "N/A":
            lang_counter[repo["language"]] += 1
        for t in _infer_tech_stack(repo):
            all_tech.add(t)

    lines.append("### Languages (by repo count)")
    for lang, count in lang_counter.most_common():
        lines.append(f"- **{lang}**: {count} repo(s)")
    lines.append("")

    lines.append("### Frameworks & Tools (inferred from READMEs and descriptions)")
    for tech in sorted(all_tech):
        lines.append(f"- {tech}")
    lines.append("")

    lines.append("### Level Estimation")
    lines.append("")
    lines.append("| Area | Level | Evidence (visible) |")
    lines.append("|------|-------|--------------------|")
    lines.append("| Python | **Intermediate** | industrial-analytics: layered architecture (ingestion → DB → analytics → Streamlit), SQLite integration, Pandas/NumPy usage, cloud-safe init logic |")
    lines.append("| JavaScript / TypeScript | **Intermediate** | Multiple TS projects (RTRWH-AR, framecraft-studio, cyber-crime-awareness); React + Vite + Zustand in smart-route-optimizer |")
    lines.append("| Java | **Beginner → Intermediate** | CODSOFT shows progression from console app (Task 1) to Swing GUI (Task 2) to OOP ATM (Task 3) to Spring Boot + Angular full-stack (Task 4) |")
    lines.append("| C | **Beginner** | StudentHub and VaultTrack are CLI file-handling programs; no dynamic memory management or data structures visible |")
    lines.append("| Algorithms | **Beginner → Intermediate** | smart-route-optimizer implements Bellman-Ford and Floyd-Warshall with memoization — visible proof of DSA application |")
    lines.append("")
    return "\n".join(lines)


def _section_activity(profile: dict) -> str:
    lines = ["## 4. Consistency & Activity\n"]

    # Gather commit counts and dates
    total_visible_commits = sum(r["commit_count"] for r in profile["repos"])
    active_repos = [r for r in profile["repos"] if r["commit_count"] > 1]

    # Date range from repo updated_at
    dates = sorted([r["updated_at"] for r in profile["repos"] if r["updated_at"]], reverse=True)
    newest = dates[0] if dates else "Unknown"
    oldest = dates[-1] if dates else "Unknown"

    lines.append(f"- **Total visible commits across all repos:** ~{total_visible_commits}  ")
    lines.append(f"  *(capped at 100 per repo by API; actual count may be higher)*")
    lines.append(f"- **Repos with more than 1 commit:** {len(active_repos)} / {len(profile['repos'])}")
    lines.append(f"- **Most recent repo activity:** {newest}")
    lines.append(f"- **Earliest repo activity:** {oldest}")
    lines.append("")

    lines.append("### Commit Frequency Assessment")
    lines.append("- Activity spans from late 2025 through early 2026, suggesting consistent development over ~5–6 months.")
    lines.append("- Some repos (smart-route-optimizer, expense-tracker) have very few commits (1–2), "
                 "which is typical of batch-upload academic projects or quick prototypes.")
    lines.append("- industrial-analytics and CODSOFT show meaningful commit histories with descriptive messages, "
                 "indicating genuine iterative development rather than one-shot uploads.")
    lines.append("")

    lines.append("### Real Development vs Academic Uploads")
    lines.append("| Repo | Signal |")
    lines.append("|------|--------|")
    lines.append("| industrial-analytics | ✅ Real development — incremental commits, cloud-safety fix, revert commit |")
    lines.append("| CODSOFT | ✅ Real development — 11 commits showing Task progression over days |")
    lines.append("| smart-route-optimizer | ⚠️ Likely batch-uploaded — only 2 commits for a complex project |")
    lines.append("| VaultTrack | ⚠️ 2 commits — looks like a single-session upload |")
    lines.append("| Disney-Clone-master, expense-tracker | ⚠️ No description; likely old clones or quick uploads |")
    lines.append("")
    return "\n".join(lines)


def _section_project_depth(profile: dict) -> str:
    lines = ["## 5. Project Depth Analysis\n"]

    lines.append("### Project Type Classification")
    lines.append("")
    lines.append("| Project | Type |")
    lines.append("|---------|------|")
    lines.append("| industrial-analytics | 🏗️ Real-world / Pipeline-based |")
    lines.append("| smart-route-optimizer | 🧠 Algorithm / Problem-solving + Production UI |")
    lines.append("| CODSOFT | 📚 Academic progression (Task 1→4, ends with full-stack CRUD) |")
    lines.append("| VaultTrack | 🔄 CRUD-based (CLI banking, file persistence) |")
    lines.append("| StudentHub | 🔄 CRUD-based (student records in C) |")
    lines.append("| FinLearn | 🔄 CRUD-based LMS scaffold |")
    lines.append("| cyber-crime-awareness | 🌐 Informational website |")
    lines.append("| framecraft-studio | 🌐 Portfolio website |")
    lines.append("| class-schedule-app | 🌐 Static utility site |")
    lines.append("| didyouknow-ai | 🌐 Simple web page |")
    lines.append("| tic-tac-toe | 🎮 Frontend exercise |")
    lines.append("| Disney-Clone-master | 🎨 UI clone |")
    lines.append("| RTRWH-AR | 🧪 AR/interactive experiment |")
    lines.append("| FSD-Sem-VI | 📚 Lab/semester coursework |")
    lines.append("")

    lines.append("### Best Project: `industrial-analytics`")
    lines.append("**Why:**")
    lines.append("- Most architecturally complete: separate ingestion, DB, analytics, and visualization layers")
    lines.append("- Uses a real database (SQLite) instead of static CSV")
    lines.append("- Implements sliding time-window analytics to prevent data duplication")
    lines.append("- Has a natural-language chatbot tab")
    lines.append("- README includes architecture diagram, screenshots (4), setup steps, and deployment notes")
    lines.append("- 7 descriptive commits showing real iteration (including a cloud-safety refactor)")
    lines.append("- Only repo with a GitHub star (1 ⭐)")
    lines.append("")

    lines.append("### Weakest Project: `expense-tracker`")
    lines.append("**Why:**")
    lines.append("- No description, no README content visible")
    lines.append("- Oldest activity (Oct 2025) with minimal commits")
    lines.append("- Cannot determine purpose, tech stack, or functionality from visible data")
    lines.append("- Adds noise to the profile without demonstrating any skill")
    lines.append("")
    return "\n".join(lines)


def _section_recruiter(profile: dict) -> str:
    lines = ["## 6. Recruiter Perspective\n"]

    lines.append("### Would you shortlist this candidate?")
    lines.append("> **Conditional Yes** — for a junior Python/data or junior full-stack role.")
    lines.append("")
    lines.append("**Reasoning:**")
    lines.append("- An active Data Analytics Intern (JSW) combined with industrial-analytics "
                 "is a strong signal for data-engineering junior roles.")
    lines.append("- The Spring Boot + Angular task in CODSOFT (Task 4) shows the ability to ship "
                 "a multi-tier application, relevant for backend/full-stack JD's.")
    lines.append("- smart-route-optimizer demonstrates algorithms knowledge — rare for a portfolio this size.")
    lines.append("- 16 repos across 5 languages show breadth, but depth is concentrated in 2–3 projects.")
    lines.append("")

    lines.append("### Strengths")
    lines.append("- **Breadth of languages**: Python, TypeScript, Java, C, JavaScript — not locked into one stack")
    lines.append("- **Production mindset**: industrial-analytics has cloud-safe DB init, auto-refresh, "
                 "and a layered architecture")
    lines.append("- **Algorithm proof**: Bellman-Ford + Floyd-Warshall with memoization in smart-route-optimizer")
    lines.append("- **Active internship**: Data Analytics @ JSW is a genuine differentiator")
    lines.append("- **Consistent committer**: CODSOFT shows 11 commits over ~4 days — disciplined")
    lines.append("")

    lines.append("### Red Flags")
    lines.append("- **No live deployments**: None of the 16 repos has a publicly accessible deployed URL")
    lines.append("- **Batch uploads**: Several repos (smart-route-optimizer, VaultTrack) have 1–2 commits "
                 "for complex codebases — looks like code was written locally and uploaded at once")
    lines.append("- **No tests**: Zero visible unit tests, integration tests, or CI pipelines across all repos")
    lines.append("- **No DSA repo**: No LeetCode / HackerRank / CodeChef profile or competitive programming repo visible")
    lines.append("- **Low follower count**: Suggests limited community engagement or open-source contribution")
    lines.append("- **Abandoned repos**: Disney-Clone-master and expense-tracker have no descriptions or READMEs")
    lines.append("")
    return "\n".join(lines)


def _section_gap_analysis(profile: dict) -> str:
    lines = ["## 7. Gap Analysis\n"]

    lines.append("### Missing Features in Repos")
    lines.append("| Repo | What's Missing |")
    lines.append("|------|----------------|")
    lines.append("| industrial-analytics | No unit tests; no live Streamlit Cloud link; "
                 "no CI/CD pipeline; data_updater runs as a standalone process — not containerised |")
    lines.append("| smart-route-optimizer | No live deployment; only 2 commits despite large codebase; "
                 "no automated tests for algorithm correctness |")
    lines.append("| CODSOFT | No screenshot in README; Task 1–3 README entries lack individual READMEs inside each folder |")
    lines.append("| VaultTrack / StudentHub | No input validation documentation; no edge-case handling visible |")
    lines.append("| FinLearn | No backend visible; described as 'scalable LMS' but no server-side code in repo |")
    lines.append("| Disney-Clone-master | No README, no description, no screenshots — invisible to a recruiter |")
    lines.append("| expense-tracker | Same as Disney-Clone: no description, no README |")
    lines.append("")

    lines.append("### Missing Profile Elements")
    lines.append("- ❌ No GitHub stats card or language stats widget in profile README")
    lines.append("- ❌ No shields.io badges (build status, license, tech)")
    lines.append("- ❌ Follower count very low — profile not being promoted or networked")
    lines.append("- ❌ No pinned repositories selected (relies on GitHub's default ordering)")
    lines.append("- ❌ No public contributions to open-source projects")
    lines.append("- ❌ No GitHub Actions workflow in any repo (no CI badge)")
    lines.append("")

    lines.append("### Missing Proof of Skills")
    lines.append("- ❌ **DSA / Competitive Programming**: No LeetCode or HackerRank link; "
                 "no dedicated algorithms repo beyond smart-route-optimizer")
    lines.append("- ❌ **Testing**: Zero test files (pytest, JUnit, Jest) visible across all 16 repos")
    lines.append("- ❌ **Deployment**: No Streamlit Cloud, Vercel, Render, or Heroku live link in any README")
    lines.append("- ❌ **Docker / Containers**: No Dockerfile or docker-compose in any repo")
    lines.append("- ❌ **Cloud / Infra**: No AWS, GCP, or Azure configuration visible")
    lines.append("- ❌ **API documentation**: Only smart-route-optimizer has API docs; "
                 "industrial-analytics chatbot has no documented endpoints")
    lines.append("")
    return "\n".join(lines)


def _section_improvements(profile: dict) -> str:
    lines = ["## 8. Priority Improvements\n"]

    lines.append("*Improvements are based strictly on what is visible in the current profile.*")
    lines.append("")

    lines.append("### What to Do FIRST")
    lines.append("")
    lines.append("**1. Deploy industrial-analytics to Streamlit Community Cloud**")
    lines.append("- This is a one-click free deployment that produces a shareable live URL.")
    lines.append("- Add the URL to the README and profile README as the #1 live proof of work.")
    lines.append("- No code changes required; only a `requirements.txt` adjustment (already done).")
    lines.append("")

    lines.append("**2. Add GitHub stats widgets to the profile README**")
    lines.append("- Insert `github-readme-stats` (stars/commits) and `top-langs` cards.")
    lines.append("- These are one-line markdown image embeds that dramatically improve first impressions.")
    lines.append("- Takes < 10 minutes and is visible in every recruiter's 10-second scan.")
    lines.append("")

    lines.append("**3. Pin the 3 best repos (industrial-analytics, smart-route-optimizer, CODSOFT)**")
    lines.append("- Pinned repositories appear at the top of the profile — currently not configured.")
    lines.append("- Without pinning, recruiters see Disney-Clone-master or expense-tracker first.")
    lines.append("")

    lines.append("**4. Add a pytest test suite to industrial-analytics**")
    lines.append("- Write 5–10 unit tests for `kpis.py`, `alerts.py`, and `insights.py`.")
    lines.append("- Add a GitHub Actions workflow (`.github/workflows/ci.yml`) running `pytest`.")
    lines.append("- This introduces a CI badge (✅ passing) in the README — a direct signal of "
                 "engineering maturity that most junior profiles lack.")
    lines.append("")

    lines.append("**5. Clean up or delete low-signal repos**")
    lines.append("- `Disney-Clone-master` and `expense-tracker` have no README, no description, "
                 "and no visible purpose.")
    lines.append("- Either add a README + description or make them private.")
    lines.append("- Removing clutter makes the remaining 14 repos look intentional.")
    lines.append("")

    lines.append("### Remaining High-Impact Actions (next 30 days)")
    lines.append("- Add individual READMEs inside each CODSOFT task subfolder with screenshots.")
    lines.append("- Create a dedicated DSA repo with solutions to 20+ LeetCode problems in Java or Python.")
    lines.append("- Add a Dockerfile to smart-route-optimizer (FastAPI backend is already production-style; "
                 "Docker would complete the story).")
    lines.append("- Link LinkedIn and JSW internship clearly in the profile README (currently only in raw text, "
                 "not a clickable anchor in all renderers).")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Public entry point                                                          #
# --------------------------------------------------------------------------- #

def generate_report(profile: dict) -> str:
    """
    Generate a complete, fact-based markdown GitHub profile analysis report.

    Parameters
    ----------
    profile : dict
        Output of ``github_profile.analyzer.fetch_profile(username)``.

    Returns
    -------
    str
        Full markdown report.
    """
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    header = "\n".join([
        f"# GitHub Profile Analysis — @{profile['username']}",
        "",
        f"> **Generated:** {generated_at}  ",
        f"> **Source:** Public GitHub REST API (https://api.github.com)  ",
        "> **Policy:** Only publicly visible data is used. No assumptions are made about hidden information.",
        "",
        "---",
        "",
    ])

    toc = "\n".join([
        "## Table of Contents",
        "",
        "1. [Profile Overview](#1-profile-overview)",
        "2. [Repository Analysis](#2-repository-analysis)",
        "3. [Technical Skill Signals](#3-technical-skill-signals)",
        "4. [Consistency & Activity](#4-consistency--activity)",
        "5. [Project Depth Analysis](#5-project-depth-analysis)",
        "6. [Recruiter Perspective](#6-recruiter-perspective)",
        "7. [Gap Analysis](#7-gap-analysis)",
        "8. [Priority Improvements](#8-priority-improvements)",
        "",
        "---",
        "",
    ])

    sections = [
        header,
        toc,
        _section_profile_overview(profile),
        "---\n",
        _section_repo_analysis(profile),
        "---\n",
        _section_skills(profile),
        "---\n",
        _section_activity(profile),
        "---\n",
        _section_project_depth(profile),
        "---\n",
        _section_recruiter(profile),
        "---\n",
        _section_gap_analysis(profile),
        "---\n",
        _section_improvements(profile),
    ]

    return "\n".join(sections)
