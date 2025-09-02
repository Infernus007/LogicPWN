#!/usr/bin/env python3
"""
Verification script for API documentation structure
Checks for:
- Missing files referenced in navigation
- Broken internal links
- Consistent formatting
- Proper sidebar structure
"""

import re
from pathlib import Path


def check_file_exists(docs_dir: Path, relative_path: str) -> bool:
    """Check if a documentation file exists."""
    # Convert relative path to file path
    file_path = docs_dir / f"{relative_path}.mdx"
    return file_path.exists()


def extract_links_from_markdown(content: str) -> list[str]:
    """Extract internal links from markdown content."""
    # Find markdown links [text](link)
    markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

    internal_links = []
    for text, link in markdown_links:
        if (
            link.startswith("./")
            or link.startswith("../")
            or not link.startswith("http")
        ):
            internal_links.append(link)

    return internal_links


def verify_navigation_structure(astro_config_path: Path) -> dict[str, list[str]]:
    """Verify the navigation structure in astro.config.mjs."""
    issues = {"missing_files": [], "broken_links": []}

    if not astro_config_path.exists():
        issues["missing_files"].append("astro.config.mjs not found")
        return issues

    with open(astro_config_path, encoding="utf-8") as f:
        config_content = f.read()

    # Extract slugs from sidebar configuration
    slug_pattern = r"slug:\s*['\"]([^'\"]+)['\"]"
    slugs = re.findall(slug_pattern, config_content)

    docs_dir = astro_config_path.parent / "src" / "content" / "docs"

    for slug in slugs:
        if not check_file_exists(docs_dir, slug):
            issues["missing_files"].append(f"Missing file for slug: {slug}")

    return issues


def verify_api_reference_links(docs_dir: Path) -> dict[str, list[str]]:
    """Verify links within API reference documentation."""
    issues = {"broken_links": [], "missing_files": []}

    api_ref_dir = docs_dir / "api-reference"
    if not api_ref_dir.exists():
        issues["missing_files"].append("api-reference directory not found")
        return issues

    # Check all .mdx files in api-reference
    for mdx_file in api_ref_dir.rglob("*.mdx"):
        with open(mdx_file, encoding="utf-8") as f:
            content = f.read()

        links = extract_links_from_markdown(content)
        for link in links:
            # Convert relative link to absolute path
            if link.startswith("./"):
                target_path = mdx_file.parent / link[2:]
            elif link.startswith("../"):
                target_path = mdx_file.parent / link
            else:
                continue

            # Resolve path and check if .mdx file exists
            target_path = target_path.resolve()
            if link.endswith(".mdx"):
                target_file = target_path
            else:
                target_file = target_path.with_suffix(".mdx")

            if not target_file.exists():
                issues["broken_links"].append(f"Broken link in {mdx_file.name}: {link}")

    return issues


def check_consistency(docs_dir: Path) -> dict[str, list[str]]:
    """Check for consistency in documentation structure."""
    issues = {"formatting": [], "structure": []}

    api_ref_dir = docs_dir / "api-reference"
    if not api_ref_dir.exists():
        return issues

    # Check frontmatter consistency
    required_frontmatter = ["title", "description"]

    for mdx_file in api_ref_dir.rglob("*.mdx"):
        with open(mdx_file, encoding="utf-8") as f:
            content = f.read()

        # Check frontmatter
        if not content.startswith("---"):
            issues["formatting"].append(f"Missing frontmatter in {mdx_file.name}")
            continue

        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            issues["formatting"].append(f"Invalid frontmatter in {mdx_file.name}")
            continue

        frontmatter = content[3:frontmatter_end]
        for field in required_frontmatter:
            if f"{field}:" not in frontmatter:
                issues["formatting"].append(f"Missing {field} in {mdx_file.name}")

    return issues


def main():
    """Main verification function."""
    project_root = Path(__file__).parent.parent
    astro_config = project_root / "doks" / "purple-atmosphere" / "astro.config.mjs"
    docs_dir = project_root / "doks" / "purple-atmosphere" / "src" / "content" / "docs"

    print("🔍 Verifying API Documentation Structure...")
    print("=" * 50)

    # Check navigation structure
    nav_issues = verify_navigation_structure(astro_config)

    # Check API reference links
    link_issues = verify_api_reference_links(docs_dir)

    # Check consistency
    consistency_issues = check_consistency(docs_dir)

    # Report results
    total_issues = 0

    if nav_issues["missing_files"]:
        print("❌ Navigation Issues:")
        for issue in nav_issues["missing_files"]:
            print(f"  - {issue}")
        total_issues += len(nav_issues["missing_files"])

    if link_issues["broken_links"]:
        print("❌ Broken Links:")
        for issue in link_issues["broken_links"]:
            print(f"  - {issue}")
        total_issues += len(link_issues["broken_links"])

    if link_issues["missing_files"]:
        print("❌ Missing Files:")
        for issue in link_issues["missing_files"]:
            print(f"  - {issue}")
        total_issues += len(link_issues["missing_files"])

    if consistency_issues["formatting"]:
        print("⚠️  Formatting Issues:")
        for issue in consistency_issues["formatting"]:
            print(f"  - {issue}")
        total_issues += len(consistency_issues["formatting"])

    if consistency_issues["structure"]:
        print("⚠️  Structure Issues:")
        for issue in consistency_issues["structure"]:
            print(f"  - {issue}")
        total_issues += len(consistency_issues["structure"])

    print("=" * 50)
    if total_issues == 0:
        print("✅ All checks passed! Documentation structure is consistent.")
    else:
        print(f"Found {total_issues} issue(s) that should be addressed.")

    # Quick stats
    api_ref_dir = docs_dir / "api-reference"
    if api_ref_dir.exists():
        mdx_files = list(api_ref_dir.rglob("*.mdx"))
        print(f"\n📊 Documentation Stats:")
        print(f"  - Total API reference files: {len(mdx_files)}")
        print(f"  - Directories: {len(list(api_ref_dir.rglob('*/')))}")


if __name__ == "__main__":
    main()
