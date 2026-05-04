"""
GitHub Profile Analyzer
Fetches public data from the GitHub REST API and returns a structured dict.
Only uses publicly visible data — no authentication required.
"""

import re
import requests


GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


# --------------------------------------------------------------------------- #
#  Low-level helpers                                                           #
# --------------------------------------------------------------------------- #

def _get(path: str, params: dict | None = None) -> dict | list | None:
    """Execute a GET request against the GitHub REST API."""
    try:
        response = requests.get(
            f"{GITHUB_API}{path}",
            headers=HEADERS,
            params=params,
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def _get_readme(owner: str, repo: str) -> str:
    """Return the decoded README content for a repository, or empty string."""
    data = _get(f"/repos/{owner}/{repo}/readme")
    if data and data.get("content"):
        import base64
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return ""
    return ""


def _count_commits(owner: str, repo: str, default_branch: str) -> int:
    """Estimate commit count on the default branch via the contributors stats endpoint."""
    # Use the compare endpoint trick: compare first-parent against empty tree
    data = _get(f"/repos/{owner}/{repo}/commits", params={"sha": default_branch, "per_page": 1})
    if data is None:
        return 0
    # Check the Link header for total (not accessible here), fall back to list length
    # Just return a rough count by fetching up to 100
    all_commits = _get(
        f"/repos/{owner}/{repo}/commits",
        params={"sha": default_branch, "per_page": 100},
    )
    return len(all_commits) if isinstance(all_commits, list) else 0


def _get_commit_messages(owner: str, repo: str, default_branch: str, n: int = 10) -> list[str]:
    data = _get(
        f"/repos/{owner}/{repo}/commits",
        params={"sha": default_branch, "per_page": n},
    )
    if not isinstance(data, list):
        return []
    return [c["commit"]["message"].split("\n")[0] for c in data]


def _has_screenshots(readme: str) -> bool:
    """Return True if the README references image files."""
    return bool(re.search(r"!\[.*?\]\(.*?\.(png|jpg|jpeg|gif|svg|webp)", readme, re.IGNORECASE))


def _has_setup_instructions(readme: str) -> bool:
    keywords = ["pip install", "npm install", "git clone", "how to run", "getting started", "setup"]
    lower = readme.lower()
    return any(kw in lower for kw in keywords)


def _has_live_demo(readme: str) -> bool:
    keywords = ["live demo", "demo link", "deployed", "netlify", "vercel", "streamlit.app",
                "heroku", "render.com", "live at", "live url"]
    lower = readme.lower()
    return any(kw in lower for kw in keywords)


# --------------------------------------------------------------------------- #
#  Public API                                                                  #
# --------------------------------------------------------------------------- #

def fetch_profile(username: str) -> dict:
    """Fetch and return a complete profile data dict for *username*."""
    user = _get(f"/users/{username}") or {}
    repos_raw = _get(f"/users/{username}/repos", params={"per_page": 100, "sort": "updated"}) or []

    repos = []
    for r in repos_raw:
        if r.get("fork"):
            continue  # skip forks — only original work

        name = r["name"]
        default_branch = r.get("default_branch", "main")
        readme = _get_readme(username, name)
        commit_messages = _get_commit_messages(username, name, default_branch)
        commit_count = _count_commits(username, name, default_branch)

        repos.append({
            "name": name,
            "description": r.get("description") or "",
            "url": r.get("html_url", ""),
            "language": r.get("language") or "N/A",
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "updated_at": r.get("updated_at", "")[:10],
            "created_at": r.get("pushed_at", "")[:10],
            "topics": r.get("topics", []),
            "has_readme": bool(readme),
            "readme": readme,
            "readme_length": len(readme),
            "has_screenshots": _has_screenshots(readme),
            "has_setup_instructions": _has_setup_instructions(readme),
            "has_live_demo": _has_live_demo(readme),
            "commit_count": commit_count,
            "commit_messages": commit_messages,
            "size": r.get("size", 0),
            "open_issues": r.get("open_issues_count", 0),
            "license": (r.get("license") or {}).get("name", "None"),
        })

    # Profile README (special repo username/username)
    profile_readme = _get_readme(username, username)

    return {
        "username": user.get("login", username),
        "name": user.get("name") or username,
        "bio": user.get("bio") or "",
        "company": user.get("company") or "",
        "location": user.get("location") or "",
        "blog": user.get("blog") or "",
        "email": user.get("email") or "",
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "public_repos": user.get("public_repos", 0),
        "created_at": (user.get("created_at") or "")[:10],
        "profile_url": f"https://github.com/{username}",
        "avatar_url": user.get("avatar_url", ""),
        "profile_readme": profile_readme,
        "repos": repos,
    }
