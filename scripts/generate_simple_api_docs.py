#!/usr/bin/env python3
"""
Simplified API Documentation Generator for LogicPwn

This script generates API documentation by importing modules and extracting
their docstrings, then creating Astro-compatible MDX files.
"""

import importlib
import inspect
import re
import sys
from pathlib import Path
from typing import Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def clean_docstring(docstring: str) -> str:
    """Clean and format docstring for MDX."""
    if not docstring:
        return ""

    # Remove extra indentation
    lines = docstring.strip().split("\n")
    if len(lines) == 1:
        cleaned = lines[0]
    else:
        # Find minimum indentation (excluding first line)
        min_indent = float("inf")
        for line in lines[1:]:
            if line.strip():
                min_indent = min(min_indent, len(line) - len(line.lstrip()))

        if min_indent == float("inf"):
            min_indent = 0

        # Remove common indentation
        cleaned_lines = [lines[0]]
        for line in lines[1:]:
            if line.strip():
                cleaned_lines.append(line[min_indent:])
            else:
                cleaned_lines.append("")

        cleaned = "\n".join(cleaned_lines)

    # Remove problematic Pydantic documentation links
    problematic_patterns = [
        r"\[([^\]]+)\]\(\.\.\/concepts\/[^)]+\)",  # Pydantic concept links
        r"See the [^.]*pydantic[^.]*\.",  # Pydantic references
        r"See [^.]*documentation[^.]*\.",  # Generic documentation references
    ]

    for pattern in problematic_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Fix Python REPL syntax issues
    # Replace unescaped Python REPL syntax with proper code blocks
    lines = cleaned.split("\n")
    fixed_lines = []
    in_code_block = False
    code_block_content = []

    for line in lines:
        # Check if this line starts a Python REPL session
        if line.strip().startswith(">>> ") or line.strip().startswith("... "):
            if not in_code_block:
                # Start a new code block
                in_code_block = True
                code_block_content = []
            code_block_content.append(line)
        elif (
            line.strip().startswith("<")
            and ">" in line
            and not line.strip().startswith("```")
        ) or (
            line.strip().startswith("[")
            and "]" in line
            and "<" in line
            and ">" in line
            and not line.strip().startswith("```")
        ):
            # This is likely a Python REPL output line
            if in_code_block:
                code_block_content.append(line)
            else:
                # Single output line, wrap it in a code block
                fixed_lines.append("```python")
                fixed_lines.append(line)
                fixed_lines.append("```")
        else:
            # Regular line
            if in_code_block:
                # End the current code block
                if code_block_content:
                    fixed_lines.append("```python")
                    fixed_lines.extend(code_block_content)
                    fixed_lines.append("```")
                in_code_block = False
                code_block_content = []
            fixed_lines.append(line)

    # Handle any remaining code block
    if in_code_block and code_block_content:
        fixed_lines.append("```python")
        fixed_lines.extend(code_block_content)
        fixed_lines.append("```")

    cleaned = "\n".join(fixed_lines)

    # Fix <factory> syntax issues by wrapping in code blocks
    # This handles cases where <factory> appears outside of code blocks
    # But avoid creating malformed code blocks
    factory_pattern = r"([^`\n])(<factory>)([^`\n])"
    cleaned = re.sub(factory_pattern, r"\1```python\n\2\n```\3", cleaned)

    # Clean up any malformed code blocks that might have been created
    # Remove any ```python\n<factory>\n``` patterns that are inside other code blocks
    cleaned = re.sub(r"```python\n<factory>\n```", "<factory>", cleaned)

    # Fix standalone function signatures and class definitions that contain <factory>
    # These often appear as standalone lines outside code blocks
    standalone_factory_pattern = r"^([A-Za-z_][A-Za-z0-9_]*\([^)]*<factory>[^)]*\))$"
    cleaned = re.sub(
        standalone_factory_pattern, r"```python\n\1\n```", cleaned, flags=re.MULTILINE
    )

    # Fix standalone class definitions with <factory>
    standalone_class_pattern = r"^([A-Za-z_][A-Za-z0-9_]*\([^)]*<factory>[^)]*\))$"
    cleaned = re.sub(
        standalone_class_pattern, r"```python\n\1\n```", cleaned, flags=re.MULTILINE
    )

    # Fix f-string expressions that might cause parsing issues
    # Look for lines that contain f-strings with curly braces outside code blocks
    f_string_pattern = r'^([^`]*f"[^"]*\{[^}]*\}[^"]*"[^`]*)$'
    cleaned = re.sub(
        f_string_pattern, r"```python\n\1\n```", cleaned, flags=re.MULTILINE
    )

    # Fix any remaining Python code that starts with # or import that's not in code blocks
    python_code_pattern = r"^((?:#|import|from|async def|def|class|if|for|while|try|except|with|await|return|yield|break|continue|pass|raise|assert|del|global|nonlocal|lambda)[^`]*)$"
    cleaned = re.sub(
        python_code_pattern, r"```python\n\1\n```", cleaned, flags=re.MULTILINE
    )

    # Clean up any remaining double spaces or empty lines
    cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
    cleaned = re.sub(r"  +", " ", cleaned)

    return cleaned.strip()


def format_signature(obj) -> str:
    """Get formatted signature for a function or method."""
    try:
        sig = inspect.signature(obj)
        return str(sig)
    except (ValueError, TypeError):
        return "()"


def extract_module_info(module_name: str) -> dict[str, Any]:
    """Extract information from a module."""
    try:
        module = importlib.import_module(module_name)

        info = {
            "name": module_name,
            "docstring": inspect.getdoc(module) or "",
            "classes": [],
            "functions": [],
        }

        # Get all public members
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue

            if inspect.isclass(obj):
                # Include classes if they're defined in this module or its submodules
                if obj.__module__ == module_name or (
                    obj.__module__ and obj.__module__.startswith(module_name + ".")
                ):
                    class_info = extract_class_info(obj)
                    if class_info:
                        info["classes"].append(class_info)

            elif inspect.isfunction(obj):
                # Include functions if they're defined in this module or its submodules
                if obj.__module__ == module_name or (
                    obj.__module__ and obj.__module__.startswith(module_name + ".")
                ):
                    func_info = extract_function_info(obj)
                    if func_info:
                        info["functions"].append(func_info)

        return info

    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        return None


def extract_class_info(cls) -> dict[str, Any]:
    """Extract information from a class."""
    try:
        info = {
            "name": cls.__name__,
            "docstring": inspect.getdoc(cls) or "",
            "methods": [],
            "properties": [],
            "signature": (
                format_signature(cls.__init__) if hasattr(cls, "__init__") else "()"
            ),
        }

        # Get inheritance
        bases = [base.__name__ for base in cls.__bases__ if base != object]
        info["inheritance"] = bases

        # Get methods and properties
        for name, obj in inspect.getmembers(cls):
            if name.startswith("_") and name != "__init__":
                continue

            if inspect.ismethod(obj) or inspect.isfunction(obj):
                if name != "__init__":  # Skip constructor, we handle it separately
                    method_info = extract_function_info(obj, is_method=True)
                    if method_info:
                        info["methods"].append(method_info)

            elif isinstance(obj, property):
                prop_info = {
                    "name": name,
                    "docstring": inspect.getdoc(obj) or "",
                    "type": getattr(obj.fget, "__annotations__", {}).get(
                        "return", "Any"
                    ),
                }
                info["properties"].append(prop_info)

        return info

    except Exception as e:
        print(f"Error extracting class {cls}: {e}")
        return None


def extract_function_info(func, is_method=False) -> dict[str, Any]:
    """Extract information from a function."""
    try:
        info = {
            "name": func.__name__,
            "docstring": inspect.getdoc(func) or "",
            "signature": format_signature(func),
            "is_async": inspect.iscoroutinefunction(func),
            "is_method": is_method,
        }

        return info

    except Exception as e:
        print(f"Error extracting function {func}: {e}")
        return None


def generate_placeholder_mdx(module_name: str) -> str:
    """Generate placeholder MDX content for modules that failed to import."""
    clean_name = module_name.replace("logicpwn.core.", "").replace("logicpwn.", "")

    # Create a display title that removes indian_ prefix for better readability
    display_name = clean_name
    parts = display_name.split(".")
    if len(parts) > 1 and parts[-1].startswith("indian_"):
        parts[-1] = parts[-1][7:]  # Remove "indian_" prefix
        display_name = ".".join(parts)

    title = display_name.replace("_", " ").replace(".", " ").title()

    # Determine module category for better navigation
    category = ""
    if "auth" in module_name:
        category = "Authentication"
    elif "access" in module_name:
        category = "Access Control"
    elif any(x in module_name for x in ["runner", "async"]):
        category = "Test Runner"
    elif "validator" in module_name:
        category = "Validation"
    elif "reporter" in module_name or "reporting" in module_name:
        category = "Reporting & Compliance"
    elif any(x in module_name for x in ["utils", "config", "performance", "cache"]):
        category = "Utilities"
    elif "exceptions" in module_name:
        category = "Exceptions"

    # Create consistent breadcrumb navigation
    parts = clean_name.split(".")

    # For nested modules, show parent navigation
    if len(parts) > 1:
        parent_title = parts[0].replace("_", " ").title()
        parent_path = parts[0].replace("_", "-")
        breadcrumb_nav = f"[{parent_title}](../{parent_path})"
    else:
        breadcrumb_nav = ""

    description = f"API documentation for the {title} module in LogicPwn framework"

    # Clean description to avoid YAML issues
    clean_description = description.replace("`", "").replace("\n", " ").strip()

    content = f"""---
title: {title}
description: {clean_description}
category: {category}
sidebar:
  order: {hash(module_name) % 100}
---

import {{ Code, Aside, Steps }} from '@astrojs/starlight/components';

{f"**Category:** {category}" if category else ""}
{f"**Navigation:** [API Reference](../) › {breadcrumb_nav}" if breadcrumb_nav else "**Navigation:** [API Reference](../)"}

API documentation for the `{module_name}` module.

:::note[Module Import Error]
This module could not be imported during documentation generation. This may be due to missing dependencies or import errors. The module may still be available at runtime.
:::

## Import

```python
import {module_name}
# or
from {module_name} import *
```

## Related Modules

:::card-grid
#card-grid
- **[API Reference](../)** - Complete API documentation
:::
"""

    return content


def generate_module_mdx(module_info: dict[str, Any]) -> str:
    """Generate MDX content for a module."""
    name = module_info["name"]
    clean_name = name.replace("logicpwn.core.", "").replace("logicpwn.", "")

    # Create a display title that removes indian_ prefix for better readability
    display_name = clean_name
    parts = display_name.split(".")
    if len(parts) > 1 and parts[-1].startswith("indian_"):
        parts[-1] = parts[-1][7:]  # Remove "indian_" prefix
        display_name = ".".join(parts)

    title = display_name.replace("_", " ").replace(".", " ").title()

    # Determine module category for better navigation
    category = ""
    if "auth" in name:
        category = "Authentication"
    elif "access" in name:
        category = "Access Control"
    elif any(x in name for x in ["runner", "async"]):
        category = "Test Runner"
    elif "validator" in name:
        category = "Validation"
    elif "reporter" in name or "reporting" in name:
        category = "Reporting & Compliance"
    elif any(x in name for x in ["utils", "config", "performance", "cache"]):
        category = "Utilities"
    elif "exceptions" in name:
        category = "Exceptions"

    # Generate consistent navigation breadcrumbs
    parts = clean_name.split(".")

    # For nested modules (e.g., validator.validator_api), show parent navigation
    if len(parts) > 1:
        parent_title = parts[0].replace("_", " ").title()
        parent_path = parts[0].replace("_", "-")
        breadcrumb_nav = f"[{parent_title}](../{parent_path})"
    else:
        breadcrumb_nav = ""

    # Generate frontmatter with better metadata
    # Create a more descriptive description from the docstring
    module_docstring = clean_docstring(module_info["docstring"])
    if module_docstring:
        # Extract first sentence or first line as description
        # Handle multi-line docstrings by taking the first non-empty line
        lines = [line.strip() for line in module_docstring.split("\n") if line.strip()]
        if lines:
            first_line = lines[0]
            # If it's a sentence, take just the first sentence
            if "." in first_line:
                first_sentence = first_line.split(".")[0].strip()
            else:
                first_sentence = first_line

            # Truncate if too long
            if len(first_sentence) > 100:
                first_sentence = first_sentence[:97] + "..."
            description = first_sentence
        else:
            description = (
                f"API documentation for the {title} module in LogicPwn framework"
            )
    else:
        description = f"API documentation for the {title} module in LogicPwn framework"

    # Clean description to avoid YAML issues
    clean_description = description.replace("`", "").replace("\n", " ").strip()

    # Determine which components are actually needed
    components_needed = ["Code", "Aside", "Steps"]

    # Check if we have classes or functions that would use Tabs
    has_classes = len(module_info.get("classes", [])) > 0
    has_functions = len(module_info.get("functions", [])) > 0

    if has_classes or has_functions:
        components_needed.extend(["Tabs", "TabItem"])

    components_import = ", ".join(components_needed)

    content = f"""---
title: {title}
description: {clean_description}
category: {category}
sidebar:
  order: {hash(name) % 100}
---

import {{ {components_import} }} from '@astrojs/starlight/components';

{f"**Category:** {category}" if category else ""}
{f"**Navigation:** [API Reference](../) › {breadcrumb_nav}" if breadcrumb_nav else "**Navigation:** [API Reference](../)"}

{module_docstring or f"API documentation for the `{name}` module."}

"""

    # Add import example
    content += f"""## Import

```python
import {name}
# or
from {name} import *
```

"""

    # Add classes with better formatting
    if module_info["classes"]:
        content += "## Classes\n\n"
        content += ":::note[Available Classes]\n"
        category_desc = category.lower() if category else "core functionality"
        content += (
            f"This module provides {len(module_info['classes'])} "
            f"class(es) for {category_desc}.\n"
        )
        content += ":::\n\n"

        for class_info in module_info["classes"]:
            content += generate_class_section(class_info)

    # Add functions with better formatting
    if module_info["functions"]:
        content += "## Functions\n\n"
        content += ":::note[Available Functions]\n"
        func_count = len(module_info["functions"])
        content += (
            f"This module provides {func_count} " f"function(s) for direct use.\n"
        )
        content += ":::\n\n"

        for func_info in module_info["functions"]:
            content += generate_function_section(func_info)

    # Add related modules section
    content += generate_related_modules_section(name, category)

    return content


def generate_class_section(class_info: dict[str, Any]) -> str:
    """Generate MDX section for a class."""
    name = class_info["name"]
    inheritance = (
        f" ({', '.join(class_info['inheritance'])})"
        if class_info["inheritance"]
        else ""
    )

    content = f"""### {name}

<Tabs>
<TabItem label="Overview">

```python
class {name}{inheritance}:
    \"\"\"
    {class_info['docstring'].split('.')[0] if class_info['docstring'] else 'Class documentation.'}
    \"\"\"
```

{clean_docstring(class_info['docstring']) or f"The `{name}` class provides core functionality for this module."}

</TabItem>
<TabItem label="Constructor">

```python
def __init__{class_info['signature']}
```

{f"Initialize a new instance of `{name}`." if class_info['signature'] != "()"
 else f"The `{name}` class uses default initialization."}

</TabItem>
</Tabs>

"""

    # Properties
    if class_info["properties"]:
        content += "#### Properties\n\n"
        for prop in class_info["properties"]:
            content += f"""<details>
<summary><code>{prop['name']}</code></summary>

{clean_docstring(prop['docstring']) or f"Property `{prop['name']}` of type `{prop.get('type', 'Any')}`."}

</details>

"""

    # Methods
    if class_info["methods"]:
        content += "#### Methods\n\n"
        for method in class_info["methods"]:
            content += generate_function_section(method, level=5, is_method=True)

    return content + "\n---\n\n"


def generate_function_section(
    func_info: dict[str, Any], level: int = 3, is_method: bool = False
) -> str:
    """Generate MDX section for a function."""
    prefix = "#" * level
    name = func_info["name"]

    # Add method indicator
    method_type = ""
    if is_method:
        method_type = "Method: "
    elif func_info.get("is_async", False):
        method_type = "Async Function: "
    else:
        method_type = "Function: "

    content = f"""{prefix} {name}

:::note[{method_type.rstrip(': ')}]
{f"Asynchronous method" if is_method and func_info.get('is_async', False) else
 f"Asynchronous function" if func_info.get('is_async', False) else
 f"Instance method" if is_method else "Module function"}
:::

```python
{"async " if func_info['is_async'] else ""}def {name}{func_info['signature']}
```

{clean_docstring(func_info['docstring']) or f"Documentation for `{name}` is not available."}

"""

    # Add usage example for async functions
    if func_info.get("is_async", False):
        content += "**Usage Example:**\n"
        content += "```python\n"
        content += f"result = await {name}(...)\n"
        content += "```\n\n"

    return content


def generate_related_modules_section(module_name: str, category: str) -> str:
    """Generate related modules section for cross-referencing."""
    content = "\n## Related Modules\n\n"

    # Define related modules by category
    related_by_category = {
        "Authentication": [
            ("auth", "Core authentication functionality"),
            ("auth/enhanced-auth", "Advanced authentication features"),
            ("auth/idp-integration", "Identity provider integration"),
        ],
        "Access Control": [
            ("access", "Core access control testing"),
            ("access/detector", "IDOR detection utilities"),
            ("access/enhanced-detector", "Advanced detection capabilities"),
        ],
        "Test Runner": [
            ("runner", "Core test execution"),
            ("runner/async-runner", "Asynchronous test execution"),
            ("runner/async-session-manager", "Session management"),
        ],
        "Validation": [
            ("validator", "Core validation functionality"),
            ("validator/validator-api", "Validation API"),
            ("validator/validator-models", "Validation data models"),
        ],
        "Utilities": [
            ("utils", "General utilities"),
            ("config", "Configuration management"),
            ("performance", "Performance monitoring"),
            ("cache", "Caching utilities"),
        ],
        "Reporting & Compliance": [
            ("reporter", "Core reporting functionality"),
            ("reporter/compliance", "Indian law enforcement compliance"),
            ("reporter/law-enforcement", "Law enforcement reports"),
            ("reporter/framework-mapper", "Compliance framework mapping"),
            ("reporter/integration", "Integration utilities"),
        ],
    }

    if category in related_by_category:
        related_modules = related_by_category[category]
        current_clean = module_name.replace("logicpwn.core.", "").replace(
            "logicpwn.", ""
        )
        current_path = current_clean.replace(".", "/").replace("_", "-")

        content += f":::tip[{category} Modules]\n"
        content += f"Explore other modules in the {category} category:\n\n"

        for module_path, description in related_modules:
            module_clean = module_path.replace("/", ".").replace("-", "_")
            if module_clean != current_clean:  # Don't link to self
                # Calculate proper relative path
                current_depth = current_path.count("/")
                if current_depth > 0:
                    back_path = "../" * current_depth
                    link_path = f"{back_path}{module_path}"
                else:
                    link_path = f"./{module_path}"

                module_title = (
                    module_path.replace("_", " ")
                    .replace("/", " › ")
                    .replace("-", " ")
                    .title()
                )
                content += f"- **[{module_title}]({link_path})** - {description}\n"

        content += ":::\n\n"

    return content


def generate_api_index(modules: list[str], output_dir: Path) -> None:
    """Generate the main API index page."""
    content = """---
title: API Reference
description: Complete API documentation for LogicPwn framework - authentication, access control, exploit engine, validation, and reporting modules
category: Documentation
sidebar:
  order: 1
---

import { Card, CardGrid, LinkCard } from '@astrojs/starlight/components';

# LogicPwn API Reference

Complete API documentation for all LogicPwn framework components.

## Core Modules

<CardGrid>
"""

    # Categorize modules with better organization
    categories = {
        "Authentication": {
            "description": "Authentication mechanisms, session management, and identity provider integration",
            "modules": [m for m in modules if "auth" in m],
        },
        "Access Control": {
            "description": "IDOR detection, privilege escalation testing, and access control validation",
            "modules": [m for m in modules if "access" in m],
        },
        "Test Runner": {
            "description": "Test execution, async processing, and session management",
            "modules": [m for m in modules if any(x in m for x in ["runner", "async"])],
        },
        "Validation": {
            "description": "Response validation, test result analysis, and reporting",
            "modules": [m for m in modules if "validator" in m],
        },
        "Utilities": {
            "description": "Configuration, caching, performance monitoring, and utility functions",
            "modules": [
                m
                for m in modules
                if any(x in m for x in ["utils", "config", "performance", "cache"])
            ],
        },
        "Reporting & Compliance": {
            "description": "Report generation, compliance frameworks, and law enforcement reporting",
            "modules": [m for m in modules if "reporter" in m or "reporting" in m],
        },
        "Exceptions": {
            "description": "Error handling and exception definitions",
            "modules": [m for m in modules if "exceptions" in m],
        },
    }

    for category, info in categories.items():
        category_modules = info["modules"]
        if not category_modules:
            continue

        content += f'  <Card title="{category}" icon="puzzle">\n'
        content += f'    <p>{info["description"]}</p>\n'
        content += "    <ul>\n"
        for module in category_modules:
            clean_name = module.replace("logicpwn.core.", "").replace("logicpwn.", "")
            link = clean_name.replace(".", "/").replace("_", "-")
            display_name = clean_name.replace("_", " ").replace(".", " › ").title()
            content += f'      <li><a href="./{link}">{display_name}</a></li>\n'
        content += "    </ul>\n"
        content += "  </Card>\n"

    content += """</CardGrid>

## Quick Start Examples

### Basic IDOR Detection

```python
from logicpwn.core.auth import AuthConfig, authenticate_session
from logicpwn.core.access import detect_idor_flaws

# Setup authentication
auth_config = AuthConfig(
    url="https://app.example.com/login",
    credentials={"username": "user", "password": "pass"}
)

session = authenticate_session(auth_config)

# Run IDOR detection
results = detect_idor_flaws(
    session,
    "https://app.example.com/api/users/{id}",
    test_ids=["1", "2", "3"],
    success_indicators=["user_data"],
    failure_indicators=["unauthorized"]
)
```

### Async Execution

```python
from logicpwn.core.runner.async_runner import AsyncTestRunner

# Setup async testing
runner = AsyncTestRunner(max_concurrent=5)

# Run tests asynchronously
results = await runner.run_tests([
    {"endpoint": endpoint, "test_data": test_data}
    for endpoint in endpoints
])
```

### Advanced Authentication

```python
from logicpwn.core.auth.enhanced_auth import EnhancedAuthHandler
from logicpwn.core.auth.idp_integration import IdPIntegration

# OAuth 2.0 authentication
auth_handler = EnhancedAuthHandler()
oauth_config = {
    "client_id": "your_client_id",
    "client_secret": "your_secret",
    "redirect_uri": "http://localhost:8080/callback"
}

session = await auth_handler.authenticate_oauth(oauth_config)
```

## Module Categories

<LinkCard
  title="Authentication & Sessions"
  description="Comprehensive authentication support including OAuth, SAML, JWT, and MFA"
  href="./auth"
/>

<LinkCard
  title="Access Control Testing"
  description="Advanced IDOR detection and privilege escalation testing capabilities"
  href="./access"
/>

<LinkCard
  title="Async Execution Engine"
  description="High-performance async test execution and session management"
  href="./runner"
/>

<LinkCard
  title="Validation & Reporting"
  description="Response validation, result analysis, and comprehensive reporting"
  href="./validator"
/>

:::tip[Documentation Notes]
This API reference is automatically generated from the source code. For usage examples and tutorials, see the [main documentation](/).

All async functions support standard Python `asyncio` patterns and can be used with `async`/`await` syntax.
:::

## Support

- **Issues**: Report bugs and request features on [GitHub](https://github.com/logicpwn/logicpwn/issues)
- **Discussions**: Join the community discussions
- **Documentation**: Full guides and tutorials in the main documentation
"""

    index_file = output_dir / "index.mdx"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main function."""
    # Define modules to document - only working modules without missing dependencies
    modules_to_document = [
        "logicpwn.core.auth",
        "logicpwn.core.auth.idp_integration",
        "logicpwn.core.auth.jwt_handler",
        "logicpwn.core.runner",
        "logicpwn.core.runner.async_runner",
        "logicpwn.core.runner.async_session_manager",
        "logicpwn.core.utils",
        "logicpwn.core.config",
        "logicpwn.core.cache",
        "logicpwn.core.validator",
        "logicpwn.core.validator.validator_api",
        "logicpwn.core.validator.validator_models",
        "logicpwn.core.exploit_engine",
        "logicpwn.core.exploit_engine.exploit_engine",
        "logicpwn.core.exploit_engine.security_validator",
        "logicpwn.core.exploit_engine.validation_engine",
        "logicpwn.core.exploit_engine.payload_generator",
        "logicpwn.core.exploit_engine.models",
        "logicpwn.core.stress",
        "logicpwn.core.stress.stress_tester",
        "logicpwn.core.stress.stress_core",
        "logicpwn.core.reliability",
        "logicpwn.core.reliability.circuit_breaker",
        "logicpwn.core.reliability.adaptive_rate_limiter",
        "logicpwn.core.reliability.security_metrics",
        "logicpwn.core.middleware",
        "logicpwn.core.middleware.middleware",
        "logicpwn.core.middleware.circuit_breaker",
        "logicpwn.core.logging",
        "logicpwn.core.logging.logger",
        "logicpwn.core.logging.redactor",
        "logicpwn.core.integration_utils",
        "logicpwn.exceptions",
    ]

    # Output directory
    output_dir = project_root / "docs" / "src" / "content" / "docs" / "api-reference"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating API documentation in {output_dir}")

    # Generate documentation for each module
    successful_modules = []
    for module_name in modules_to_document:
        print(f"Processing {module_name}...")

        module_info = extract_module_info(module_name)
        if not module_info:
            # Generate placeholder content for failed imports
            print(f"  ⚠️  Generating placeholder for {module_name}")
            mdx_content = generate_placeholder_mdx(module_name)
        else:
            # Generate MDX content
            mdx_content = generate_module_mdx(module_info)

        # Create output file path
        clean_name = module_name.replace("logicpwn.core.", "").replace("logicpwn.", "")
        file_parts = clean_name.split(".")

        # Create directory structure
        current_dir = output_dir
        for part in file_parts[:-1]:
            current_dir = current_dir / part.replace("_", "-")
            current_dir.mkdir(exist_ok=True)

        # Generate filename with underscores replaced by hyphens
        # Special handling for indian_* modules - remove "indian_" prefix
        final_filename = file_parts[-1]

        # Remove "indian_" prefix for reporter modules
        if final_filename.startswith("indian_"):
            final_filename = final_filename[7:]  # Remove "indian_" (7 characters)

        # Write file
        filename = final_filename.replace("_", "-") + ".mdx"
        output_file = current_dir / filename

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(mdx_content)

        successful_modules.append(module_name)
        print(f"  ✓ Generated {output_file}")

    # Generate index page
    generate_api_index(successful_modules, output_dir)
    print("  ✓ Generated index page")

    print(
        f"\nSuccessfully generated documentation for {len(successful_modules)} modules!"
    )
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
