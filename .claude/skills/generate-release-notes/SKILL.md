---
name: generate-release-notes
description: Generate and sort rippled release notes from GitHub commit history
argument-hint: --from <ref> --to <ref> [--date YYYY-MM-DD]
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# Generate rippled Release Notes

This skill generates a draft release notes blog post for a new rippled version, then sorts the entries into the correct sections.

## Step 1: Generate the raw release notes

Run the Python script from the repo root. Pass through all arguments from `$ARGUMENTS`:

```bash
python3 tools/generate-release-notes.py $ARGUMENTS
```

If the user didn't provide `--from` or `--to`, ask them for the base and target refs (tags or branches).

The script will:
- Fetch the version string from `BuildInfo.cpp`
- Fetch all commits between the two refs
- Fetch PR details (title, link, labels, files, description) via GraphQL
- Compare `features.macro` between refs to identify amendment changes
- Auto-sort amendment entries into the Amendments section
- Output all other entries as unsorted with full context

## Step 2: Review the generated file

Read the output file (path shown in script output). Note the structure:
- **Amendments section**: Contains auto-sorted entries and an HTML comment listing which amendments to include/exclude
- **Empty subsections**: Features, Breaking Changes, Bug Fixes, Refactors, Documentation, Testing, CI/Build
- **Unsorted entries**: All remaining entries below the empty subsections, with title, link, labels, files, and description for context

## Step 3: Sort unsorted entries into subsections

Move each unsorted entry into the appropriate subsection. Use these signals to categorize:

**Files changed** (strongest signal):
- Only `.github/`, `CMakeLists.txt`, `conan*`, CI config files → **CI/Build**
- Only `src/test/`, `*_test.cpp` files → **Testing**
- Only `*.md`, `docs/` files → **Documentation**

**Labels** (strong signal):
- `Amendment` label → **Amendments**
- `Bug` label → **Bug Fixes**

**Title prefixes** (medium signal):
- `fix:` → **Bug Fixes**
- `feat:` → **Features**
- `refactor:` → **Refactors**
- `docs:` → **Documentation**
- `test:` → **Testing**
- `ci:`, `build:`, `chore:` → **CI/Build**

**Description content** (when other signals are ambiguous):
- Read the PR description to understand the change's purpose

## Step 4: Reformat sorted entries

After sorting, reformat each entry to match the release notes style:

**Amendment entries** should follow this format:
```markdown
- **amendmentName**: Description of what the amendment does. ([#1234](https://github.com/XRPLF/rippled/pull/1234))
```

Additional amendment guidance:
- You can use slightly more detail for amendment descriptions, since they are the most important. Use present tense.
- Use the HTML comment in the Amendments section to decide which entries to keep or remove.
- There should only be one entry per amendment. If you decide to include multiple entries that touch the same amendment, merge them into one.

**Feature and Breaking Change entries** should follow this format:
```markdown
- Description of the change. ([#1234](https://github.com/XRPLF/rippled/pull/1234))
```

Additional feature and breaking change guidance:
- Keep the description concise. Use past tense.

**All other entries** should follow this format:
```markdown
- The title of the entry. ([#1234](https://github.com/XRPLF/rippled/pull/1234))
```

Additional guidance for all other entries:
- Minimally process the title of the entry. Fix basic capitalization and punctuation. Use past tense.

**Additional guidance**
- Check for revert/re-apply patterns and only keep the final entry state
- Add an additional one-liner to the frontmatter seo description.
- Highlight the most important aspects of the release and add a summary of the changes to the Introducing XRP Ledger Version section.

## Step 5: Clean up

- Remove empty subsections that have no entries
- Remove all HTML comments (sorting instructions)
- Do a final review of the release notes. If you see anything strange, notify the user, but don't make changes.
