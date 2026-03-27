"""
Generate rippled release notes from GitHub commit history.

Usage (from repo root):
    python3 tools/generate-release-notes.py --from release-3.0 --to release-3.1 [--date 2026-03-24] [--output path/to/file.md]

Arguments:
    --from      (required) Base ref — must match exact tag or branch to compare from.
    --to        (required) Target ref — must match exact tag or branch to compare to.
    --date      (optional) Release date in YYYY-MM-DD format. Defaults to today.
    --output    (optional) Output file path. Defaults to blog/<year>/rippled-<version>.md.

Requires: gh CLI (authenticated)
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime


# Emails to exclude from credits (Ripple employees not using @ripple.com).
# Commits from @ripple.com addresses are already filtered automatically.
EXCLUDED_EMAILS = {
    "3maisons@gmail.com",                                   # Luc des Trois Maisons
    "a1q123456@users.noreply.github.com",                   # Jingchen Wu
    "bthomee@users.noreply.github.com",                     # Bart Thomee
    "21219765+ckeshava@users.noreply.github.com",           # Chenna Keshava B S
    "gregtatcam@users.noreply.github.com",                  # Gregory Tsipenyuk
    "kuzzz99@gmail.com",                                    # Sergey Kuznetsov
    "legleux@users.noreply.github.com",                     # Michael Legleux
    "mathbunnyru@users.noreply.github.com",                 # Ayaz Salikhov
    "mvadari@gmail.com",                                    # Mayukha Vadari
    "115580134+oleks-rip@users.noreply.github.com",         # Oleksandr Pidskopnyi
    "3397372+pratikmankawde@users.noreply.github.com",      # Pratik Mankawde
    "35279399+shawnxie999@users.noreply.github.com",        # Shawn Xie
    "5780819+Tapanito@users.noreply.github.com",            # Vito Tumas
    "13349202+vlntb@users.noreply.github.com",              # Valentin Balaschenko
    "129996061+vvysokikh1@users.noreply.github.com",        # Vladislav Vysokikh
    "vvysokikh@gmail.com",                                  # Vladislav Vysokikh
}


# Pre-compiled patterns for skipping version commits
SKIP_PATTERNS = [
    re.compile(r"^Set version to", re.IGNORECASE),
    re.compile(r"^Version \d", re.IGNORECASE),
    re.compile(r"bump version to", re.IGNORECASE),
    re.compile(r"^Merge tag ", re.IGNORECASE),
]


# --- API helpers ---

def run_gh_rest(endpoint):
    """Run a gh api REST command and return parsed JSON."""
    result = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error running gh api: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def run_gh_graphql(query):
    """Run a gh api graphql command and return parsed JSON.
    Handles partial failures (e.g., missing PRs) by returning
    whatever data is available alongside errors.
    """
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        print(f"Error running graphql: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def fetch_commit_files(sha):
    """Fetch list of files changed in a commit via REST API.
    Returns empty list on failure instead of exiting.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/XRPLF/rippled/commits/{sha}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  Warning: Could not fetch files for commit {sha[:7]}", file=sys.stderr)
        return []
    data = json.loads(result.stdout)
    return [f["filename"] for f in data.get("files", [])]


# --- Data fetching ---

def fetch_version_info(ref):
    """Fetch version string and version-setting commit info in a single GraphQL call.
    Returns (version_string, formatted_commit_block).
    """
    data = run_gh_graphql(f"""
    {{
        repository(owner: "XRPLF", name: "rippled") {{
            file: object(expression: "{ref}:src/libxrpl/protocol/BuildInfo.cpp") {{
                ... on Blob {{ text }}
            }}
            ref: object(expression: "{ref}") {{
                ... on Commit {{
                    history(first: 1, path: "src/libxrpl/protocol/BuildInfo.cpp") {{
                        nodes {{
                            oid
                            message
                            author {{
                                name
                                email
                                date
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """)
    repo = data.get("data", {}).get("repository", {})

    # Extract version string from BuildInfo.cpp
    file_text = (repo.get("file") or {}).get("text", "")
    match = re.search(r'versionString\s*=\s*"([^"]+)"', file_text)
    if not match:
        print("Warning: Could not find versionString in BuildInfo.cpp. Using placeholder.", file=sys.stderr)
    version = match.group(1) if match else "TODO"

    # Extract version commit info
    nodes = (repo.get("ref") or {}).get("history", {}).get("nodes", [])
    if not nodes:
        commit_block = "commit TODO\nAuthor: TODO\nDate:   TODO\n\n    Set version to TODO"
    else:
        commit = nodes[0]
        raw_date = commit["author"]["date"]
        try:
            dt = datetime.fromisoformat(raw_date)
            formatted_date = dt.strftime("%a %b %-d %H:%M:%S %Y %z")
        except ValueError:
            formatted_date = raw_date

        name = commit["author"]["name"]
        email = commit["author"]["email"]
        sha = commit["oid"]
        message = commit["message"].split("\n")[0]
        commit_block = f"commit {sha}\nAuthor: {name} <{email}>\nDate:   {formatted_date}\n\n    {message}"

    return version, commit_block


def fetch_commits(from_ref, to_ref):
    """Fetch all commits between two refs using the GitHub compare API."""
    commits = []
    page = 1
    while True:
        data = run_gh_rest(
            f"repos/XRPLF/rippled/compare/{from_ref}...{to_ref}?per_page=250&page={page}"
        )
        batch = data.get("commits", [])
        commits.extend(batch)
        if len(batch) < 250:
            break
        page += 1
    return commits


def fetch_prs_graphql(pr_numbers):
    """Fetch PR details in batches using GitHub GraphQL API.
    Falls back to issue lookup for numbers that aren't PRs.
    Returns a dict of {number: {title, body, labels, files, type}}.
    """
    results = {}
    missing = []
    batch_size = 50
    pr_list = list(pr_numbers)

    # Fetch PRs
    for i in range(0, len(pr_list), batch_size):
        batch = pr_list[i:i + batch_size]

        fragments = []
        for pr_num in batch:
            fragments.append(f"""
                pr{pr_num}: pullRequest(number: {pr_num}) {{
                    title
                    body
                    labels(first: 10) {{
                        nodes {{ name }}
                    }}
                    files(first: 100) {{
                        nodes {{ path }}
                    }}
                }}
            """)

        query = f"""
        {{
            repository(owner: "XRPLF", name: "rippled") {{
                {"".join(fragments)}
            }}
        }}
        """

        data = run_gh_graphql(query)
        repo_data = data.get("data", {}).get("repository", {})

        for alias, pr_data in repo_data.items():
            pr_num = int(alias.removeprefix("pr"))
            if pr_data:
                results[pr_num] = {
                    "title": pr_data["title"],
                    "body": clean_pr_body(pr_data.get("body") or ""),
                    "labels": [l["name"] for l in pr_data.get("labels", {}).get("nodes", [])],
                    "files": [f["path"] for f in pr_data.get("files", {}).get("nodes", [])],
                    "type": "pull",
                }
            else:
                missing.append(pr_num)

        print(f"  Fetched {min(i + batch_size, len(pr_list))}/{len(pr_list)} PRs...")

    # Fetch missing numbers as issues
    if missing:
        print(f"  Looking up {len(missing)} missing PR numbers as Issues...")
        for i in range(0, len(missing), batch_size):
            batch = missing[i:i + batch_size]

            fragments = []
            for num in batch:
                fragments.append(f"""
                    issue{num}: issue(number: {num}) {{
                        title
                        body
                        labels(first: 10) {{
                            nodes {{ name }}
                        }}
                    }}
                """)

            query = f"""
            {{
                repository(owner: "XRPLF", name: "rippled") {{
                    {"".join(fragments)}
                }}
            }}
            """

            data = run_gh_graphql(query)
            repo_data = data.get("data", {}).get("repository", {})

            for alias, issue_data in repo_data.items():
                if issue_data:
                    num = int(alias.removeprefix("issue"))
                    results[num] = {
                        "title": issue_data["title"],
                        "body": clean_pr_body(issue_data.get("body") or ""),
                        "labels": [l["name"] for l in issue_data.get("labels", {}).get("nodes", [])],
                        "type": "issues",
                    }

    return results


# --- Utilities ---

def clean_pr_body(text):
    """Strip HTML comments and PR template boilerplate from body text."""
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Remove unchecked checkbox lines, keep checked ones
    text = re.sub(r"^- \[ \] .+$", "", text, flags=re.MULTILINE)
    # Remove all markdown headings
    text = re.sub(r"^#{1,6} .+$", "", text, flags=re.MULTILINE)
    # Convert bare GitHub URLs to markdown links
    text = re.sub(r"(?<!\()https://github\.com/XRPLF/rippled/(pull|issues)/(\d+)(#[^\s)]*)?", r"[#\2](https://github.com/XRPLF/rippled/\1/\2\3)", text)
    # Convert remaining bare PR/issue references (#1234) to full GitHub links
    text = re.sub(r"(?<!\[)#(\d+)(?!\])", r"[#\1](https://github.com/XRPLF/rippled/pull/\1)", text)
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pr_number(commit_message):
    """Extract PR number from commit message like 'Title (#1234)'."""
    match = re.search(r"#(\d+)", commit_message)
    return int(match.group(1)) if match else None


def should_skip(title):
    """Check if a commit should be skipped."""
    return any(pattern.search(title) for pattern in SKIP_PATTERNS)


def is_amendment(files):
    """Check if any file in the list is features.macro."""
    return any("features.macro" in f for f in files)


# --- Formatting ---

def format_commit_entry(sha, title, body="", files=None):
    """Format an entry linked to a commit (no PR/Issue found)."""
    short_sha = sha[:7]
    url = f"https://github.com/XRPLF/rippled/commit/{sha}"
    parts = [
        f"- **{title.strip()}**",
        f"  - Link: [{short_sha}]({url})",
    ]
    if files:
        parts.append(f"  - Files: {', '.join(files)}")
    if body:
        desc = re.sub(r"\s+", " ", clean_pr_body(body)).strip()
        if desc:
            parts.append(f"  - Description: {desc}")
    return "\n".join(parts)


def format_uncategorized_entry(pr_number, title, labels, body, files=None, link_type="pull"):
    """Format an uncategorized entry with full context for AI sorting."""
    url = f"https://github.com/XRPLF/rippled/{link_type}/{pr_number}"
    parts = [
        f"- **{title.strip()}**",
        f"  - Link: [#{pr_number}]({url})",
    ]
    if labels:
        parts.append(f"  - Labels: {', '.join(labels)}")
    if files:
        parts.append(f"  - Files: {', '.join(files)}")
    if body:
        # Collapse to single line to prevent markdown formatting conflicts
        desc = re.sub(r"\s+", " ", body).strip()
        if desc:
            parts.append(f"  - Description: {desc}")
    return "\n".join(parts)


def generate_markdown(version, release_date, amendment_entries, entries, authors, version_commit):
    """Generate the full markdown release notes."""
    year = release_date.split("-")[0]
    parts = []

    parts.append(f"""---
category: {year}
date: "{release_date}"
template: '../../@theme/templates/blogpost'
seo:
    title: Introducing XRP Ledger version {version}
    description: rippled version {version} is now available.
labels:
    - rippled Release Notes
markdown:
    editPage:
        hide: true
---
# Introducing XRP Ledger version {version}

Version {version} of `rippled`, the reference server implementation of the XRP Ledger protocol, is now available.


## Action Required

If you run an XRP Ledger server, upgrade to version {version} as soon as possible to ensure service continuity.


## Install / Upgrade

On supported platforms, see the [instructions on installing or updating `rippled`](../../docs/infrastructure/installation/index.md).

| Package | SHA-256 |
|:--------|:--------|
| [RPM for Red Hat / CentOS (x86-64)](https://repos.ripple.com/repos/rippled-rpm/stable/rippled-{version}-1.el9.x86_64.rpm) | `TODO` |
| [DEB for Ubuntu / Debian (x86-64)](https://repos.ripple.com/repos/rippled-deb/pool/stable/rippled_{version}-1_amd64.deb) | `TODO` |

For other platforms, please [build from source](https://github.com/XRPLF/rippled/blob/master/BUILD.md). The most recent commit in the git log should be the change setting the version:

```text
{version_commit}
```


## Full Changelog
""")

    # Amendments section (auto-sorted by features.macro detection)
    parts.append("\n### Amendments\n")
    for entry in amendment_entries:
        parts.append(entry)

    # Remaining empty subsection headings for manual/AI sorting
    sections = [
        "Features", "Breaking Changes", "Bug Fixes",
        "Refactors", "Documentation", "Testing", "CI/Build",
    ]
    for section in sections:
        parts.append(f"\n### {section}\n")

    # Uncategorized entries with full context
    parts.append("<!-- Sort the entries below into the subsections above. Remove this comment after sorting. -->\n")
    for entry in entries:
        parts.append(entry)

    # Credits
    parts.append("\n\n## Credits\n")
    if authors:
        parts.append("The following RippleX teams and GitHub users contributed to this release:\n")
    else:
        parts.append("The following RippleX teams contributed to this release:\n")
    parts.append("- RippleX Engineering")
    parts.append("- RippleX Docs")
    parts.append("- RippleX Product")
    for author in sorted(authors):
        parts.append(f"- {author}")

    parts.append("""

## Bug Bounties and Responsible Disclosures

We welcome reviews of the `rippled` code and urge researchers to responsibly disclose any issues they may find.

To report a bug, please send a detailed report to: <bugs@xrpl.org>
""")

    return "\n".join(parts)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Generate rippled release notes")
    parser.add_argument("--from", dest="from_ref", required=True, help="Base ref (tag or branch)")
    parser.add_argument("--to", dest="to_ref", required=True, help="Target ref (tag or branch)")
    parser.add_argument("--date", help="Release date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--output", help="Output file path (default: blog/<year>/rippled-<version>.md)")
    args = parser.parse_args()

    args.date = args.date or date.today().isoformat()

    print(f"Fetching version info from {args.to_ref}...")
    version, version_commit = fetch_version_info(args.to_ref)
    print(f"Version: {version}")

    year = args.date.split("-")[0]
    output_path = args.output or f"blog/{year}/rippled-{version}.md"

    print(f"Fetching commits: {args.from_ref}...{args.to_ref}")
    commits = fetch_commits(args.from_ref, args.to_ref)
    print(f"Found {len(commits)} commits")

    # Extract unique PR (in rare cases Issues) numbers and track authors
    pr_numbers = {}
    pr_shas = {}       # PR/issue number → commit SHA (for file lookups on Issues)
    pr_bodies = {}     # PR/issue number → commit body (for fallback descriptions)
    orphan_commits = []  # Commits with no PR/Issues link
    authors = set()

    for commit in commits:
        full_message = commit["commit"]["message"]
        message = full_message.split("\n")[0]
        body = "\n".join(full_message.split("\n")[1:]).strip()
        sha = commit["sha"]
        author = commit["commit"]["author"]["name"]
        email = commit["commit"]["author"].get("email", "")

        # Skip Ripple employees from credits
        login = (commit.get("author") or {}).get("login")
        if not email.lower().endswith("@ripple.com") and email not in EXCLUDED_EMAILS:
            if login:
                authors.add(f"@{login}")
            else:
                authors.add(author)

        if should_skip(message):
            continue

        pr_number = extract_pr_number(message)
        if pr_number:
            pr_numbers[pr_number] = message
            pr_shas[pr_number] = sha
            pr_bodies[pr_number] = body
        else:
            orphan_commits.append({"sha": sha, "message": message, "body": body})

    print(f"Unique PRs after filtering: {len(pr_numbers)}")
    if orphan_commits:
        print(f"Commits without PR or Issue linked: {len(orphan_commits)}")
    print(f"Building changelog entries...")

    # Fetch all PR details in batches via GraphQL
    pr_details = fetch_prs_graphql(list(pr_numbers.keys()))

    # Build entries, sorting amendments automatically
    amendment_entries = []
    entries = []
    for pr_number, commit_msg in pr_numbers.items():
        pr_data = pr_details.get(pr_number)

        if pr_data:
            title = pr_data["title"]
            body = pr_data.get("body", "")
            labels = pr_data.get("labels", [])
            files = pr_data.get("files", [])
            link_type = pr_data.get("type", "pull")

            # For issues (no files from GraphQL), fetch files from the commit
            if not files and pr_number in pr_shas:
                print(f"  Building entry for Issue #{pr_number} via commit...")
                files = fetch_commit_files(pr_shas[pr_number])

            # Auto-sort: entries touching features.macro go to Amendments
            if is_amendment(files):
                entry = format_uncategorized_entry(pr_number, title, labels, body, link_type=link_type)
                amendment_entries.append(entry)
            else:
                entry = format_uncategorized_entry(pr_number, title, labels, body, files, link_type)
                entries.append(entry)
        else:
            # Fallback to commit lookup for invalid PR and Issues link
            sha = pr_shas[pr_number]
            print(f"  #{pr_number} not found as PR or Issue, building from commit {sha[:7]}...")
            files = fetch_commit_files(sha)
            if is_amendment(files):
                entry = format_commit_entry(sha, commit_msg, pr_bodies[pr_number])
                amendment_entries.append(entry)
            else:
                entry = format_commit_entry(sha, commit_msg, pr_bodies[pr_number], files)
                entries.append(entry)

    # Build entries for orphan commits (no PR/Issue linked)
    for orphan in orphan_commits:
        sha = orphan["sha"]
        print(f"  Building commit-only entry for {sha[:7]}...")
        files = fetch_commit_files(sha)
        if is_amendment(files):
            entry = format_commit_entry(sha, orphan["message"], orphan["body"])
            amendment_entries.append(entry)
        else:
            entry = format_commit_entry(sha, orphan["message"], orphan["body"], files)
            entries.append(entry)

    # Generate markdown
    markdown = generate_markdown(version, args.date, amendment_entries, entries, authors, version_commit)

    # Write output
    with open(output_path, "w") as f:
        f.write(markdown)

    print(f"\nRelease notes written to: {output_path}")


if __name__ == "__main__":
    main()
