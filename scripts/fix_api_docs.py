#!/usr/bin/env python3
"""
Fix Astro API documentation by:
1. Removing source code sections
2. Correcting exploit engine examples
3. Adding better examples throughout
"""

import re
from pathlib import Path


def remove_source_code_sections(content: str) -> str:
    """Remove source code tip sections from MDX content"""
    # Pattern to match the source code tip blocks
    pattern = r":::tip\[Source Code\].*?:::\n\n"
    return re.sub(pattern, "", content, flags=re.DOTALL)


def fix_markdown_formatting(content: str) -> str:
    """Fix markdown formatting issues in generated documentation"""

    # Fix !!! abstract syntax to proper Astro/Starlight format
    content = re.sub(
        r'!!! abstract "([^"]*)"\s*\n\n', r'<Aside type="note" title="\1">\n\n', content
    )

    # Fix !!! note syntax
    content = re.sub(
        r'!!! note "([^"]*)"\s*\n\n', r'<Aside type="note" title="\1">\n\n', content
    )

    # Fix !!! warning syntax
    content = re.sub(
        r'!!! warning "([^"]*)"\s*\n\n',
        r'<Aside type="warning" title="\1">\n\n',
        content,
    )

    # Fix !!! info syntax
    content = re.sub(
        r'!!! info "([^"]*)"\s*\n\n', r'<Aside type="info" title="\1">\n\n', content
    )

    # Fix standalone !!! abstract without quotes
    content = re.sub(r"!!! abstract\s*\n\n", r'<Aside type="note">\n\n', content)

    # Fix standalone !!! note without quotes
    content = re.sub(r"!!! note\s*\n\n", r'<Aside type="note">\n\n', content)

    # Fix broken Pydantic model documentation
    content = re.sub(
        r'!!! abstract "Usage Documentation"\s*\n\nA base class for creating Pydantic models\.',
        r'<Aside type="note" title="Base Model">\n\nThis is a Pydantic BaseModel class that provides data validation and serialization capabilities.\n\n</Aside>',
        content,
    )

    # Fix broken links in docstrings
    content = re.sub(r"\[([^\]]+)\]\(\.\.\/concepts\/[^)]+\)", r"\1", content)

    # Fix malformed docstring content
    content = re.sub(r'\[Models\]\(\s*\n\s*"""', r'"""', content)

    # Fix !!! syntax inside code blocks (remove them)
    content = re.sub(r'(\s*)!!! abstract "([^"]*)"\s*\n', r"\1# \2\n", content)

    content = re.sub(r'(\s*)!!! note "([^"]*)"\s*\n', r"\1# \2\n", content)

    content = re.sub(r'(\s*)!!! warning "([^"]*)"\s*\n', r"\1# \2\n", content)

    content = re.sub(r'(\s*)!!! info "([^"]*)"\s*\n', r"\1# \2\n", content)

    # Fix standalone !!! syntax inside code blocks
    content = re.sub(r"(\s*)!!! abstract\s*\n", r"\1# Documentation\n", content)

    content = re.sub(r"(\s*)!!! note\s*\n", r"\1# Note\n", content)

    # Fix broken docstring patterns
    content = re.sub(
        r'"""\s*\n\s*!!! abstract "([^"]*)"\s*\n\s*"""',
        r'"""\n    \1\n    """',
        content,
    )

    # Remove problematic <Aside> tags that are causing errors
    # Replace with simple markdown formatting
    content = re.sub(
        r"<Aside[^>]*>(?!.*</Aside>)(.*?)(?=\n\n|\n##|\n###|\n####|\n#####|\n######|\Z)",
        r"**Note:** \1\n\n",
        content,
        flags=re.DOTALL,
    )

    # Also remove any remaining unclosed <Aside> tags
    content = re.sub(r"<Aside[^>]*>(?!.*</Aside>)", "", content)

    # Fix JSON syntax in code blocks that's causing MDX parsing errors
    # Escape curly braces in JSON objects within code blocks
    content = re.sub(
        r'(\{[^}]*"url"[^}]*\})',
        lambda m: m.group(1).replace("{", "&#123;").replace("}", "&#125;"),
        content,
    )

    return content


def fix_exploit_engine_examples(content: str) -> str:
    """Fix exploit engine examples to match the corrected YAML"""

    # Replace outdated exploit chain examples with corrected ones
    old_example = r"```yaml\nexploit_chain:.*?```"

    new_example = """```yaml
# LogicPWN Simple Prototype Pollution → SSTI Exploit Chain
name: "Simple Prototype Pollution → SSTI Chain"
description: "Basic exploit chain demonstrating prototype pollution leading to SSTI injection"
session_state:
  target_base_url: "http://localhost:3000"

steps:
  # Step 1: Prototype Pollution via settings[debug]=true
  - name: "Prototype Pollution Attack"
    description: "Exploit prototype pollution vulnerability via URL parameters"
    request_config:
      method: "GET"
      url: "http://localhost:3000/?settings%5Bdebug%5D=true"
      headers:
        User-Agent: "LogicPWN/1.0 Security Scanner"
    success_indicators:
      - "200"
    failure_indicators:
      - "404"
      - "500"
    retry_count: 2

  # Step 2: Template Engine Testing
  - name: "Template Engine Detection"
    description: "Test template engine response via POST request"
    request_config:
      method: "POST"
      url: "http://localhost:3000/theme"
      headers:
        User-Agent: "LogicPWN/1.0 Security Scanner"
    success_indicators:
      - "200"
    failure_indicators:
      - "404"
      - "500"
    retry_count: 2

  # Step 3: SSTI Injection Attack
  - name: "SSTI Injection Attack"
    description: "Perform Server-Side Template Injection with JSON payload"
    request_config:
      method: "POST"
      url: "http://localhost:3000/theme"
      headers:
        Content-Type: "application/json"
        User-Agent: "LogicPWN/1.0 Security Scanner"
      json_data:
        message: "p Hello from injection!"
    success_indicators:
      - "200"
      - "Hello from injection"
    failure_indicators:
      - "404"
      - "500"
    retry_count: 2
```"""

    return re.sub(old_example, new_example, content, flags=re.DOTALL)


def add_better_examples(content: str) -> str:
    """Add better examples throughout the documentation"""

    # Add practical examples after import sections
    if "## Import" in content and "from logicpwn" in content:
        import_section = re.search(r"## Import.*?```\n", content, re.DOTALL)
        if import_section:
            practical_examples = """

## Quick Examples

### Basic Usage

```python
from logicpwn.core.exploit_engine import load_exploit_chain_from_file, run_exploit_chain
import requests

# Load and execute a simple exploit chain
session = requests.Session()
chain = load_exploit_chain_from_file("examples/simple_exploit_corrected.yaml")
results = run_exploit_chain(session, chain)

# Analyze results
for result in results:
    print(f"Step: {result.step_name}")
    print(f"Status: {result.status}")
    print(f"Time: {result.execution_time:.2f}s")
```

### Real-World IDOR Testing

```python
from logicpwn.core.access import detect_idor_flaws
from logicpwn.core.auth import AuthConfig, authenticate_session

# Setup authentication
auth_config = AuthConfig(
    url="https://api.example.com/login",
    credentials={"username": "user", "password": "pass"},
    success_indicators=["access_token"]
)

session = authenticate_session(auth_config)

# Test for IDOR vulnerabilities
results = detect_idor_flaws(
    session,
    "https://api.example.com/users/{id}/profile",
    test_ids=["1", "2", "3", "admin", "999"],
    success_indicators=["user_data", "profile"],
    failure_indicators=["unauthorized", "403"]
)
```

"""
            content = content.replace(
                import_section.group(), import_section.group() + practical_examples
            )

    return content


def process_mdx_file(file_path: Path) -> None:
    """Process a single MDX file"""
    print(f"Processing {file_path}...")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Apply fixes
    content = remove_source_code_sections(content)
    content = fix_markdown_formatting(content)
    content = fix_exploit_engine_examples(content)
    content = add_better_examples(content)

    # Only write if content changed
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ Updated {file_path.name}")
    else:
        print(f"  - No changes needed for {file_path.name}")


def main():
    """Main function to fix all API documentation"""
    print("🔧 Fixing Astro API Documentation")
    print("=" * 50)

    # API reference directory
    api_docs_dir = (
        Path(__file__).parent.parent
        / "docs"
        / "src"
        / "content"
        / "docs"
        / "api-reference"
    )

    if not api_docs_dir.exists():
        print(f"❌ Error: API docs directory not found: {api_docs_dir}")
        return

    # Process all MDX files
    mdx_files = list(api_docs_dir.rglob("*.mdx"))
    print(f"Found {len(mdx_files)} MDX files to process")
    print()

    for mdx_file in mdx_files:
        process_mdx_file(mdx_file)

    print()
    print("✅ API documentation fixes completed!")
    print()
    print("Summary of changes:")
    print("  • Removed source code tip sections")
    print("  • Fixed markdown formatting issues (!!! syntax)")
    print("  • Updated exploit engine examples")
    print("  • Added practical usage examples")
    print("  • Improved documentation quality")


if __name__ == "__main__":
    main()
