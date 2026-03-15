"""
Deterministic spec crawler — no LLM required.

Reads companies.yaml and fetches each spec directly using the GitHub REST API.
Used as the fallback when ANTHROPIC_API_KEY is not set.
"""
from pathlib import Path

from crawler.config import load_registry
from crawler.tools import content_sha256, existing_sha256, fetch_file, list_dir, write_file


def run() -> None:
    registry = load_registry()
    updated = unchanged = errors = 0

    for company in registry.companies:
        for spec in company.specs:
            try:
                # Resolve the list of (repo_path, output_path) pairs to fetch
                pairs: list[tuple[str, str]] = []

                if spec.path and spec.output:
                    pairs.append((spec.path, spec.output))

                elif spec.path_pattern and spec.output_dir:
                    files = list_dir(spec.repo, spec.path_pattern)
                    for f in files:
                        output_path = str(Path(spec.output_dir) / f["name"])
                        pairs.append((f["path"], output_path))

                for repo_path, output_path in pairs:
                    content, _ = fetch_file(spec.repo, repo_path)
                    if content_sha256(content) == existing_sha256(output_path):
                        print(f"  [unchanged] {output_path}")
                        unchanged += 1
                    else:
                        write_file(output_path, content)
                        print(f"  [updated]   {output_path}")
                        updated += 1

            except Exception as exc:
                print(f"  [error]     {company.name}: {exc}")
                errors += 1

    print(f"\nDone — updated: {updated}, unchanged: {unchanged}, errors: {errors}")
