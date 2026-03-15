"""
Deterministic consumer notifier — no LLM required.

Implements the same 5-phase flow as the agent: detect changed specs, detect
breaking changes, discover consumer repos, check usage, create issues.
Used as the fallback when ANTHROPIC_API_KEY is not set.
"""
from notifier.tools import (
    check_consumer_usage_plain,
    create_issue_plain,
    detect_breaking_changes_plain,
    get_changed_specs_plain,
    search_consumer_repos_plain,
)


def _issue_title(display_name: str, description: str) -> str:
    short = description[:80] + "..." if len(description) > 80 else description
    return f"[DriftaBot] Breaking change in {display_name} API: {short}"


def _issue_body(
    display_name: str,
    spec_type: str,
    bc: dict,
    matched_files: list[str],
) -> str:
    files_md = "\n".join(f"- `{f}`" for f in matched_files) or "_(no specific files identified)_"
    return f"""## Breaking API Change Detected — {display_name} {spec_type} API

Hi! DriftaBot detected a breaking change in the **{display_name}** API that may affect this repository.

### What changed
**{bc['description']}**

- **Type:** `{bc['type']}`
- **Path:** `{bc.get('path', '')}` `{bc.get('method', '')}`
- **Location:** `{bc.get('location', '')}`
- **Severity:** Breaking

### Affected files in this repo
{files_md}

### Recommended action
Please review the files above and update any references to the changed endpoint or field.
See the {display_name} API changelog for migration guidance.

---
*This issue was automatically created by [DriftaBot](https://github.com/DriftaBot/specs).
If this is a false positive, please close the issue.*
"""


def run() -> None:
    # Phase 1: detect changed specs
    changed = get_changed_specs_plain()
    if not changed:
        print("No spec changes detected. Notifier exiting.")
        return

    print(f"Detected {len(changed)} changed spec file(s).")

    total_breaking = 0
    total_repos = 0
    total_affected = 0
    total_created = 0
    total_errors = 0

    # Group breaking changes by company (Phase 2)
    companies_breaks: dict[str, dict] = {}  # company_name -> {display_name, spec_type, changes}
    for entry in changed:
        result = detect_breaking_changes_plain(entry["company"], entry["spec_type"], entry["path"])
        if result.get("error"):
            print(f"  [error] {entry['company']}: {result['error']}")
            continue
        if result["breaking_count"] == 0:
            print(f"  [no breaks] {entry['path']}")
            continue
        print(f"  [breaking] {entry['path']}: {result['breaking_count']} breaking change(s)")
        total_breaking += result["breaking_count"]
        key = entry["company"]
        if key not in companies_breaks:
            companies_breaks[key] = {
                "display_name": entry["display_name"],
                "spec_type": entry["spec_type"],
                "changes": [],
            }
        companies_breaks[key]["changes"].extend(result["breaking_changes"])

    # Phases 3–5: per-company loop
    for company_name, info in companies_breaks.items():
        display = info["display_name"]
        spec_type = info["spec_type"]
        breaking_changes = info["changes"]

        # Phase 3: find consumer repos
        repos = search_consumer_repos_plain(company_name)
        total_repos += len(repos)
        print(f"  [consumers] {company_name}: {len(repos)} repo(s) found")

        for repo in repos:
            for bc in breaking_changes:
                # Phase 4: check if repo uses the affected feature
                usage = check_consumer_usage_plain(
                    repo["full_name"],
                    bc.get("path", ""),
                    bc.get("location", ""),
                    bc.get("description", ""),
                )
                if not usage.get("affected"):
                    continue
                total_affected += 1

                # Phase 5: create issue
                title = _issue_title(display, bc["description"])
                body = _issue_body(display, spec_type, bc, usage["matched_files"])
                result = create_issue_plain(repo["full_name"], title, body)
                if result["status"] == "created":
                    total_created += 1
                    print(f"  [issue created] {repo['full_name']}: {result['url']}")
                elif result["status"] == "duplicate":
                    print(f"  [duplicate]     {repo['full_name']}: {result['url']}")
                else:
                    total_errors += 1
                    print(f"  [error]         {repo['full_name']}: {result.get('error')}")

    print(
        f"\nDone — breaking changes: {total_breaking}, "
        f"consumer repos found: {total_repos}, "
        f"affected: {total_affected}, "
        f"issues created: {total_created}, "
        f"errors: {total_errors}"
    )
