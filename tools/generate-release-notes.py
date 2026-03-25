"""
Generate rippled release notes from GitHub commit history.
The version number is auto-detected from BuildInfo.cpp in the --to ref.

Usage (from repo root):
    python3 tools/generate-release-notes.py --from 3.0.0 --to 3.1.0 [--date 2026-03-24] [--output path/to/file.md]

Arguments:
    --from      (required) Base ref — tag or branch to compare from.
    --to        (required) Target ref — tag or branch to compare to.
    --date      (optional) Release date in YYYY-MM-DD format. Defaults to today.
    --output    (optional) Output file path. Defaults to blog/<year>/rippled-<version>.md.

Requires: gh CLI (authenticated)
"""

import argparse
import base64
import json
import re
import subprocess
import sys
from datetime import date


# Subsection headings for the changelog (empty until sorted)
SECTIONS = [
    "Amendments",
    "Features",
    "Breaking Changes",
    "Bug Fixes",
    "Refactors",
    "Documentation",
    "Testing",
    "CI/Build",
]


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
    """Run a gh api graphql command and return parsed JSON."""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error running graphql: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def fetch_version(ref):
    """Fetch the version string from BuildInfo.cpp at the given ref."""
    result = subprocess.run(
        ["gh", "api", f"repos/XRPLF/rippled/contents/src/libxrpl/protocol/BuildInfo.cpp?ref={ref}",
         "--jq", ".content"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error fetching BuildInfo.cpp: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    content = base64.b64decode(result.stdout.strip()).decode()
    match = re.search(r'versionString\s*=\s*"([^"]+)"', content)
    if not match:
        print("Error: Could not find versionString in BuildInfo.cpp", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


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
    Returns a dict of {pr_number: {title, body, labels}}.
    """
    results = {}
    batch_size = 50
    pr_list = list(pr_numbers)

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
            if pr_data:
                pr_num = int(alias.removeprefix("pr"))
                results[pr_num] = {
                    "title": pr_data["title"],
                    "body": strip_html_comments(pr_data.get("body", "")),
                    "labels": [l["name"] for l in pr_data.get("labels", {}).get("nodes", [])],
                }

        print(f"  Fetched {min(i + batch_size, len(pr_list))}/{len(pr_list)} PRs...")

    return results


def strip_html_comments(text):
    """Strip HTML comment blocks (<!-- ... -->) from text."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()


def extract_pr_number(commit_message):
    """Extract PR number from commit message like 'Title (#1234)'."""
    match = re.search(r"#(\d+)", commit_message)
    return int(match.group(1)) if match else None


def should_skip(title):
    """Check if a commit should be skipped."""
    skip_patterns = [
        r"^Set version to",
        r"^Revert \"",
    ]
    return any(re.match(pattern, title) for pattern in skip_patterns)


def format_uncategorized_entry(pr_number, title, labels, body):
    """Format an uncategorized entry with full context for AI sorting."""
    pr_url = f"https://github.com/XRPLF/rippled/pull/{pr_number}"
    entry = f"- **{title}**\n"
    entry += f"  - PR: [#{pr_number}]({pr_url})\n"
    if labels:
        entry += f"  - Labels: {', '.join(labels)}\n"
    if body:
        desc = body.split("\n\n")[0].strip()  # First paragraph
        desc = re.sub(r"\s+", " ", desc)  # Collapse whitespace
        if desc:
            entry += f"  - Description: {desc}\n"
    return entry


def generate_markdown(version, release_date, entries, authors, version_commit):
    """Generate the full markdown release notes."""
    year = release_date.split("-")[0]

    md = f"""---
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

"""

    # Empty subsection headings for manual/AI sorting
    for section in SECTIONS:
        md += f"\n### {section}\n\n"

    # Uncategorized entries with full context
    md += "\n### Uncategorized\n\n"
    md += "<!-- Sort the entries below into the subsections above. -->\n\n"
    for entry in entries:
        md += entry + "\n"

    # Credits
    md += "\n\n## Credits\n\nThe following RippleX teams and GitHub users contributed to this release:\n\n- RippleX Engineering\n- RippleX Docs\n-RippleX Product"
    for author in sorted(authors):
        md += f"- {author}\n"

    md += """

## Bug Bounties and Responsible Disclosures

We welcome reviews of the `rippled` code and urge researchers to responsibly disclose any issues they may find.

To report a bug, please send a detailed report to: <bugs@xrpl.org>
"""

    return md


def main():
    parser = argparse.ArgumentParser(description="Generate rippled release notes")
    parser.add_argument("--from", dest="from_ref", required=True, help="Base ref (tag or branch)")
    parser.add_argument("--to", dest="to_ref", required=True, help="Target ref (tag or branch)")
    parser.add_argument("--date", help="Release date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--output", help="Output file path (default: blog/<year>/rippled-<version>.md)")
    args = parser.parse_args()

    args.date = args.date or date.today().isoformat()

    print(f"Fetching version from BuildInfo.cpp at {args.to_ref}...")
    version = fetch_version(args.to_ref)
    print(f"Version: {version}")

    year = args.date.split("-")[0]
    output_path = args.output or f"blog/{year}/rippled-{version}.md"

    print(f"Fetching commits: {args.from_ref}...{args.to_ref}")
    commits = fetch_commits(args.from_ref, args.to_ref)
    print(f"Found {len(commits)} commits")

    # Extract unique PR numbers and track authors
    pr_numbers = {}
    authors = set()
    version_commit = "commit TODO\nAuthor: TODO\nDate:   TODO\n\n    Set version to " + version

    for commit in commits:
        message = commit["commit"]["message"].split("\n")[0]
        author = commit["commit"]["author"]["name"]
        gh_user = commit.get("author", {})
        if gh_user:
            authors.add(f"@{gh_user.get('login', author)}")
        else:
            authors.add(author)

        # Capture version commit info
        if message.startswith("Set version to"):
            sha = commit["sha"]
            date_str = commit["commit"]["author"]["date"]
            version_commit = f"commit {sha}\nAuthor: {author}\nDate:   {date_str}\n\n    {message}"

        pr_number = extract_pr_number(message)
        if pr_number and pr_number not in pr_numbers:
            pr_numbers[pr_number] = message

    # Filter out skippable commits
    filtered_prs = {
        num: msg for num, msg in pr_numbers.items()
        if not should_skip(msg)
    }

    print(f"Unique PRs after filtering: {len(filtered_prs)}")
    print(f"Fetching PR details via GraphQL...")

    # Fetch all PR details in batches via GraphQL
    pr_details = fetch_prs_graphql(list(filtered_prs.keys()))

    # Build uncategorized entries with full context
    entries = []
    for pr_number, commit_msg in filtered_prs.items():
        pr_data = pr_details.get(pr_number)
        title = pr_data["title"] if pr_data else commit_msg
        body = pr_data.get("body", "") if pr_data else ""
        labels = pr_data.get("labels", []) if pr_data else []

        entry = format_uncategorized_entry(pr_number, title, labels, body)
        entries.append(entry)

    # Generate markdown
    markdown = generate_markdown(version, args.date, entries, authors, version_commit)

    # Write output
    with open(output_path, "w") as f:
        f.write(markdown)

    print(f"\nRelease notes written to: {output_path}")
    print(f"Total entries: {len(entries)}")


if __name__ == "__main__":
    main()
