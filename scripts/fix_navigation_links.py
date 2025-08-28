#!/usr/bin/env python3
"""
Fix navigation links in existing API documentation files.
This script removes source code sections and fixes navigation breadcrumbs.
"""

import re
from pathlib import Path


def fix_navigation_in_file(file_path: Path) -> bool:
    """Fix navigation and remove source code sections in a single MDX file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remove source code tip sections
        content = re.sub(
            r":::tip\[Source Code\].*?:::\n\n", "", content, flags=re.DOTALL
        )

        # Fix navigation patterns
        # Pattern 1: Navigation with complex breadcrumbs
        content = re.sub(
            r"\*\*Navigation:\*\* \[API Reference\]\(\.\./\) › .*",
            lambda m: fix_navigation_breadcrumb(file_path),
            content,
        )

        # Pattern 2: Navigation with incorrect relative paths (like ../auth)
        content = re.sub(
            r"\*\*Navigation:\*\* \[API Reference\]\(\.\./[^)]+\) › "
            r"\[([^\]]+)\]\(\.\./[^)]+\)",
            r"**Navigation:** [API Reference](../) › [\1](../)",
            content,
        )

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_navigation_breadcrumb(file_path: Path) -> str:
    """Generate correct navigation breadcrumb based on file path."""
    # Get relative path from api-reference directory
    parts = file_path.parts
    api_ref_index = -1
    for i, part in enumerate(parts):
        if part == "api-reference":
            api_ref_index = i
            break

    if api_ref_index == -1:
        return "**Navigation:** [API Reference](../)"

    # Get path components after api-reference
    path_parts = parts[api_ref_index + 1:]

    # Remove file extension
    if path_parts and path_parts[-1].endswith(".mdx"):
        path_parts = path_parts[:-1]

    # If it's nested (e.g., validator/validator-api.mdx)
    if len(path_parts) > 1:
        parent = path_parts[0].replace("-", " ").title()
        return f"**Navigation:** [API Reference](../) › [{parent}](../)"
    else:
        return "**Navigation:** [API Reference](../)"


def main():
    """Main function to fix all API documentation files."""
    # Find the API reference directory
    project_root = Path(__file__).parent.parent
    api_ref_dir = (
        project_root
        / "doks"
        / "purple-atmosphere"
        / "src"
        / "content"
        / "docs"
        / "api-reference"
    )

    if not api_ref_dir.exists():
        print(f"API reference directory not found: {api_ref_dir}")
        return

    print(f"Fixing navigation links in {api_ref_dir}")

    # Find all MDX files
    mdx_files = list(api_ref_dir.rglob("*.mdx"))

    fixed_count = 0
    for mdx_file in mdx_files:
        print(f"Processing {mdx_file.relative_to(api_ref_dir)}...")
        if fix_navigation_in_file(mdx_file):
            fixed_count += 1
            print("  ✓ Fixed navigation")
        else:
            print("  - No changes needed")

    print(f"\nFixed navigation in {fixed_count} out of {len(mdx_files)} files!")


if __name__ == "__main__":
    main()
