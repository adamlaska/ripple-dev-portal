#!/usr/bin/env python3
"""
Generate rippled release notes from GitHub commit history.

Usage:
    python tools/generate-release-notes.py --from release-3.0 --to release-3.1 --version 3.1.0 --date 2026-03-24

Requires: gh CLI (authenticated)
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict


# Section order for the changelog
SECTIONS = [
    "Amendments",
    "Features",
    "Breaking Changes",
    "Bug Fixes",
    "Refactors",
    "Documentation",
    "Testing",
    "CI/Build",
    "Unsorted",
]


def run_gh(args):
    """Run a gh CLI command and return parsed JSON."""
    result = subprocess.run(
        ["gh", "api", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error running gh api: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def fetch_commits(from_ref, to_ref):
    """Fetch all commits between two refs using the GitHub compare API.
    The compare endpoint returns up to 250 commits. For larger ranges,
    paginate using the page query parameter.
    """
    commits = []
    page = 1
    while True:
        data = run_gh([
            f"repos/XRPLF/rippled/compare/{from_ref}...{to_ref}?per_page=250&page={page}",
        ])
        batch = data.get("commits", [])
        commits.extend(batch)
        if len(batch) < 250:
            break
        page += 1
    return commits


def extract_pr_number(commit_message):
    """Extract PR number from commit message like 'Title (#1234)'."""
    match = re.search(r"#(\d+)", commit_message)
    return int(match.group(1)) if match else None


def fetch_pr(pr_number):
    """Fetch PR details from GitHub."""
    try:
        return run_gh([f"repos/XRPLF/rippled/pulls/{pr_number}"])
    except SystemExit:
        return None


def should_skip(title):
    """Check if a commit should be skipped."""
    skip_patterns = [
        r"^Set version to",
        r"^Revert \"",
    ]
    return any(re.match(pattern, title) for pattern in skip_patterns)


def categorize(title, body=""):
    """Categorize a PR based on its title and commit message prefix."""
    title_lower = title.lower()

    # Strip conventional commit prefix for matching
    stripped = re.sub(r"^(fix|feat|docs|test|ci|build|refactor|breaking)(\(.+?\))?:\s*", "", title, flags=re.IGNORECASE)

    # Check commit message prefix first
    prefix_match = re.match(r"^(fix|feat|docs|test|ci|build|refactor|breaking)(\(.+?\))?:", title, re.IGNORECASE)
    prefix = prefix_match.group(1).lower() if prefix_match else None

    # Amendment detection: CamelCase names that look like amendment names
    # e.g., "fixTokenEscrowV1", "featureBatch", "LendingProtocol"
    amendment_pattern = r"\b(fix[A-Z]\w+|feature[A-Z]\w+|[A-Z][a-z]+[A-Z]\w*Protocol|[A-Z][a-z]+[A-Z]\w*V\d+)\b"
    if re.search(amendment_pattern, title):
        # Check if this looks like an amendment change (not just a code fix mentioning a function)
        amendment_keywords = ["amendment", "enable", "disable", "supported", "feature", "open for voting"]
        if any(kw in title_lower for kw in amendment_keywords) or re.search(r"^(fix[A-Z]|feature[A-Z])", stripped):
            return "Amendments"

    if prefix == "fix":
        return "Bug Fixes"
    if prefix == "feat":
        return "Features"
    if prefix == "docs":
        return "Documentation"
    if prefix == "test":
        return "Testing"
    if prefix in ("ci", "build"):
        return "CI/Build"
    if prefix == "refactor":
        return "Refactors"
    if prefix == "breaking":
        return "Breaking Changes"

    # Fallback: keyword matching on title
    if any(kw in title_lower for kw in ["breaking change", "breaking:"]):
        return "Breaking Changes"

    fix_keywords = ["fix ", "fixed ", "fixes "]
    if any(title_lower.startswith(kw) for kw in fix_keywords):
        return "Bug Fixes"

    if any(kw in title_lower for kw in ["add ", "added ", "implement", "introduce"]):
        return "Features"

    if any(kw in title_lower for kw in ["refactor", "restructure", "decouple", "clean up", "cleanup", "replace"]):
        return "Refactors"

    if any(kw in title_lower for kw in ["readme", "typo", "comment", "spelling", "documentation"]):
        return "Documentation"

    if any(kw in title_lower for kw in ["test", "doctest"]):
        return "Testing"

    ci_keywords = ["ci", "github action", "cmake", "conan", "docker", "workflow", "pre-commit", "codecov", "build"]
    if any(kw in title_lower for kw in ci_keywords):
        return "CI/Build"

    return "Unsorted"


def format_entry(title, pr_number):
    """Format a single changelog entry."""
    # Capitalize first letter
    title = title[0].upper() + title[1:] if title else title

    # Strip conventional commit prefix for display
    title = re.sub(r"^(fix|feat|docs|test|ci|build|refactor|breaking)(\(.+?\))?:\s*", "", title, flags=re.IGNORECASE)

    # Re-capitalize after stripping prefix
    title = title[0].upper() + title[1:] if title else title

    # Ensure title ends with a period
    if title and not title.endswith("."):
        title = title.rstrip(".") + "."

    pr_url = f"https://github.com/XRPLF/rippled/pull/{pr_number}"
    return f"- {title} ([#{pr_number}]({pr_url}))"


def format_amendment_entry(title, pr_number):
    """Format an amendment changelog entry with bold name."""
    # Try to extract the amendment name (CamelCase identifier)
    match = re.search(r"\b(fix[A-Z]\w+|feature[A-Z]\w+|[A-Z][a-z]+[A-Z]\w*)\b", title)
    if match:
        amendment_name = match.group(1)
        # Strip prefix and amendment name from title for the description
        desc = re.sub(r"^(fix|feat|docs|test|ci|build|refactor|breaking)(\(.+?\))?:\s*", "", title, flags=re.IGNORECASE)
        desc = desc[0].upper() + desc[1:] if desc else desc
        if desc and not desc.endswith("."):
            desc = desc.rstrip(".") + "."
        pr_url = f"https://github.com/XRPLF/rippled/pull/{pr_number}"
        return f"- **{amendment_name}**: {desc} ([#{pr_number}]({pr_url}))"

    # Fallback to regular format
    return format_entry(title, pr_number)


def generate_markdown(version, date, sections, authors, version_commit):
    """Generate the full markdown release notes."""
    year = date.split("-")[0]

    md = f"""---
category: {year}
date: "{date}"
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

    for section in SECTIONS:
        entries = sections.get(section, [])
        if not entries:
            continue
        md += f"\n### {section}\n\n"
        for entry in entries:
            md += entry + "\n"
        md += "\n"

    # Credits
    md += "\n## Credits\n\nThe following GitHub users contributed to this release:\n\n"
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
    parser.add_argument("--version", required=True, help="Version string (e.g., 3.1.0)")
    parser.add_argument("--date", required=True, help="Release date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file path (default: blog/<year>/rippled-<version>.md)")
    args = parser.parse_args()

    year = args.date.split("-")[0]
    output_path = args.output or f"blog/{year}/rippled-{args.version}.md"

    print(f"Fetching commits: {args.from_ref}...{args.to_ref}")
    commits = fetch_commits(args.from_ref, args.to_ref)
    print(f"Found {len(commits)} commits")

    # Extract unique PR numbers and track authors
    pr_numbers = {}
    authors = set()
    version_commit = "commit TODO\nAuthor: TODO\nDate:   TODO\n\n    Set version to " + args.version

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
    print(f"Fetching PR details...")

    # Fetch PR details and categorize
    sections = defaultdict(list)

    for i, (pr_number, commit_msg) in enumerate(filtered_prs.items(), 1):
        pr_data = fetch_pr(pr_number)
        title = pr_data["title"] if pr_data else commit_msg
        body = pr_data.get("body", "") if pr_data else ""

        category = categorize(title, body)

        if category == "Amendments":
            entry = format_amendment_entry(title, pr_number)
        else:
            entry = format_entry(title, pr_number)

        sections[category].append(entry)

        if i % 10 == 0:
            print(f"  Processed {i}/{len(filtered_prs)} PRs...")

    # Generate markdown
    markdown = generate_markdown(args.version, args.date, sections, authors, version_commit)

    # Write output
    with open(output_path, "w") as f:
        f.write(markdown)

    print(f"\nRelease notes written to: {output_path}")
    print(f"\nSummary:")
    for section in SECTIONS:
        count = len(sections.get(section, []))
        if count:
            print(f"  {section}: {count}")


if __name__ == "__main__":
    main()
