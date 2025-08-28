#!/usr/bin/env python3
"""
API Documentation Generator for LogicPwn Astro Documentation

This script automatically extracts docstrings, type hints, and class/function
signatures from Python code and generates Astro-compatible MDX files.

Features:
- Extracts docstrings with proper formatting
- Preserves type hints and signatures
- Generates navigation structure
- Creates cross-references
- Handles inheritance and method resolution
- Supports custom templates
"""

import ast
import inspect
import os
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, get_type_hints
from dataclasses import dataclass, field
import importlib
import importlib.util

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    module: str
    docstring: Optional[str] = None
    methods: List['FunctionInfo'] = field(default_factory=list)
    properties: List['PropertyInfo'] = field(default_factory=list)
    inheritance: List[str] = field(default_factory=list)
    signature: Optional[str] = None
    source_file: Optional[str] = None


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    module: str
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    is_async: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    source_file: Optional[str] = None


@dataclass
class PropertyInfo:
    """Information about a property."""
    name: str
    docstring: Optional[str] = None
    property_type: Optional[str] = None
    getter: bool = True
    setter: bool = False


@dataclass
class ModuleInfo:
    """Information about a module."""
    name: str
    docstring: Optional[str] = None
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    source_file: Optional[str] = None


class APIDocumentationExtractor:
    """Extracts API documentation from Python modules."""
    
    def __init__(self, package_path: str, output_dir: str):
        self.package_path = Path(package_path)
        self.output_dir = Path(output_dir)
        self.modules: Dict[str, ModuleInfo] = {}
        
    def extract_all_modules(self) -> Dict[str, ModuleInfo]:
        """Extract documentation from all modules in the package."""
        for py_file in self.package_path.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
                
            module_name = self._get_module_name(py_file)
            try:
                module_info = self.extract_module(py_file, module_name)
                if module_info:
                    self.modules[module_name] = module_info
            except Exception as e:
                print(f"Error extracting {module_name}: {e}")
                
        return self.modules
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative_path = file_path.relative_to(self.package_path.parent)
        parts = list(relative_path.parts)
        
        # Remove .py extension
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
            
        # Handle __init__.py files
        if parts[-1] == "__init__":
            parts = parts[:-1]
            
        return ".".join(parts)
    
    def extract_module(self, file_path: Path, module_name: str) -> Optional[ModuleInfo]:
        """Extract documentation from a single module."""
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Parse the AST for additional information
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            tree = ast.parse(source)
            
            module_info = ModuleInfo(
                name=module_name,
                docstring=inspect.getdoc(module),
                source_file=str(file_path)
            )
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, module, module_name)
                    if class_info:
                        module_info.classes.append(class_info)
                        
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Only top-level functions
                    if hasattr(node, 'col_offset') and node.col_offset == 0:
                        func_info = self._extract_function_info(node, module, module_name)
                        if func_info:
                            module_info.functions.append(func_info)
            
            return module_info
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def _extract_class_info(self, node: ast.ClassDef, module: Any, module_name: str) -> Optional[ClassInfo]:
        """Extract information about a class."""
        try:
            # Get the actual class object
            class_obj = getattr(module, node.name, None)
            if not class_obj:
                return None
                
            class_info = ClassInfo(
                name=node.name,
                module=module_name,
                docstring=inspect.getdoc(class_obj),
                signature=self._get_class_signature(class_obj),
                inheritance=[base.name for base in node.bases if isinstance(base, ast.Name)]
            )
            
            # Extract methods and properties
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                    method_info = self._extract_method_info(item, class_obj, module_name)
                    if method_info:
                        class_info.methods.append(method_info)
                        
            # Extract properties using inspection
            for name, obj in inspect.getmembers(class_obj):
                if isinstance(obj, property):
                    prop_info = PropertyInfo(
                        name=name,
                        docstring=inspect.getdoc(obj),
                        property_type=self._get_type_annotation(class_obj, name),
                        setter=obj.fset is not None
                    )
                    class_info.properties.append(prop_info)
            
            return class_info
            
        except Exception as e:
            print(f"Error extracting class {node.name}: {e}")
            return None
    
    def _extract_function_info(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                             module: Any, module_name: str) -> Optional[FunctionInfo]:
        """Extract information about a function."""
        try:
            func_obj = getattr(module, node.name, None)
            if not func_obj:
                return None
                
            func_info = FunctionInfo(
                name=node.name,
                module=module_name,
                docstring=inspect.getdoc(func_obj),
                signature=self._get_function_signature(func_obj),
                is_async=isinstance(node, ast.AsyncFunctionDef),
                parameters=self._extract_parameters(func_obj)
            )
            
            return func_info
            
        except Exception as e:
            print(f"Error extracting function {node.name}: {e}")
            return None
    
    def _extract_method_info(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                           class_obj: Any, module_name: str) -> Optional[FunctionInfo]:
        """Extract information about a class method."""
        try:
            method_obj = getattr(class_obj, node.name, None)
            if not method_obj:
                return None
                
            func_info = FunctionInfo(
                name=node.name,
                module=module_name,
                docstring=inspect.getdoc(method_obj),
                signature=self._get_function_signature(method_obj),
                is_async=isinstance(node, ast.AsyncFunctionDef),
                is_classmethod=isinstance(method_obj, classmethod),
                is_staticmethod=isinstance(method_obj, staticmethod),
                parameters=self._extract_parameters(method_obj)
            )
            
            return func_info
            
        except Exception as e:
            print(f"Error extracting method {node.name}: {e}")
            return None
    
    def _get_class_signature(self, class_obj: Any) -> str:
        """Get class constructor signature."""
        try:
            sig = inspect.signature(class_obj.__init__)
            params = []
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                params.append(str(param))
            return f"({', '.join(params)})"
        except:
            return "()"
    
    def _get_function_signature(self, func_obj: Any) -> str:
        """Get function signature."""
        try:
            if isinstance(func_obj, (classmethod, staticmethod)):
                func_obj = func_obj.__func__
            sig = inspect.signature(func_obj)
            return str(sig)
        except:
            return "()"
    
    def _extract_parameters(self, func_obj: Any) -> List[Dict[str, Any]]:
        """Extract parameter information."""
        try:
            if isinstance(func_obj, (classmethod, staticmethod)):
                func_obj = func_obj.__func__
                
            sig = inspect.signature(func_obj)
            params = []
            
            for name, param in sig.parameters.items():
                param_info = {
                    'name': name,
                    'annotation': str(param.annotation) if param.annotation != inspect.Parameter.empty else None,
                    'default': str(param.default) if param.default != inspect.Parameter.empty else None,
                    'kind': param.kind.name
                }
                params.append(param_info)
                
            return params
        except:
            return []
    
    def _get_type_annotation(self, obj: Any, attr_name: str) -> Optional[str]:
        """Get type annotation for an attribute."""
        try:
            type_hints = get_type_hints(obj)
            return str(type_hints.get(attr_name))
        except:
            return None


class AstroMDXGenerator:
    """Generates Astro-compatible MDX files from extracted API documentation."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_docs(self, modules: Dict[str, ModuleInfo]) -> None:
        """Generate all documentation files."""
        # Create directory structure
        api_dir = self.output_dir / "api-reference"
        api_dir.mkdir(exist_ok=True)
        
        # Generate index page
        self.generate_api_index(modules, api_dir / "index.mdx")
        
        # Generate module documentation
        for module_name, module_info in modules.items():
            self.generate_module_docs(module_info, api_dir)
    
    def generate_api_index(self, modules: Dict[str, ModuleInfo], output_file: Path) -> None:
        """Generate the main API reference index."""
        content = """---
title: API Reference
description: Complete API documentation for LogicPwn framework
---

import { Card, CardGrid } from '@astrojs/starlight/components';

# LogicPwn API Reference

Complete API documentation for all LogicPwn framework components.

## Core Modules

<CardGrid>
"""
        
        # Group modules by category
        categories = self._categorize_modules(modules)
        
        for category, category_modules in categories.items():
            content += f'  <Card title="{category}" icon="code">\n'
            for module_name, module_info in category_modules.items():
                clean_name = module_name.replace("logicpwn.core.", "")
                content += f'    - [{clean_name}](./{clean_name.replace(".", "/")})\n'
            content += '  </Card>\n'
        
        content += """</CardGrid>

## Quick Navigation

### Authentication & Sessions
- [`logicpwn.core.auth`](./auth) - Authentication and session management
- [`logicpwn.core.auth.oauth_handler`](./auth/oauth-handler) - OAuth 2.0 flows
- [`logicpwn.core.auth.saml_handler`](./auth/saml-handler) - SAML SSO
- [`logicpwn.core.auth.jwt_handler`](./auth/jwt-handler) - JWT token handling

### Access Control & IDOR Detection  
- [`logicpwn.core.access`](./access) - Access control testing
- [`logicpwn.core.access.detector`](./access/detector) - IDOR detection
- [`logicpwn.core.access.enhanced_detector`](./access/enhanced-detector) - Advanced detection

### Exploit Engine
- [`logicpwn.core.exploit_engine`](./exploit-engine) - Exploit orchestration
- [`logicpwn.core.async_runner`](./async-runner) - Async request execution

### Reporting & Compliance
- [`logicpwn.core.reporter`](./reporter) - Core reporting functionality
- [`logicpwn.core.reporter.indian_compliance`](./reporter/indian-compliance) - Indian law enforcement compliance
- [`logicpwn.core.reporter.indian_law_enforcement`](./reporter/indian-law-enforcement) - Law enforcement reports
- [`logicpwn.core.reporter.framework_mapper`](./reporter/framework-mapper) - Compliance framework mapping

### Utilities
- [`logicpwn.core.utils`](./utils) - Utility functions
- [`logicpwn.core.performance`](./performance) - Performance monitoring
- [`logicpwn.core.config`](./config) - Configuration management
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_module_docs(self, module_info: ModuleInfo, base_dir: Path) -> None:
        """Generate documentation for a single module."""
        # Create directory structure
        module_parts = module_info.name.split('.')
        if module_parts[0] == 'logicpwn' and len(module_parts) > 1:
            module_parts = module_parts[2:]  # Remove 'logicpwn.core'
        
        if not module_parts:
            return
            
        module_dir = base_dir
        for part in module_parts[:-1]:
            module_dir = module_dir / part
            module_dir.mkdir(exist_ok=True)
        
        # Generate module file
        filename = module_parts[-1].replace('_', '-') + '.mdx'
        output_file = module_dir / filename
        
        content = self._generate_module_content(module_info)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_module_content(self, module_info: ModuleInfo) -> str:
        """Generate MDX content for a module."""
        clean_name = module_info.name.replace('logicpwn.core.', '')
        title = clean_name.replace('_', ' ').replace('.', ' ').title()
        
        content = f"""---
title: {title}
description: {self._get_module_description(module_info)}
---

import {{ Code, Aside }} from '@astrojs/starlight/components';

# {title}

{self._format_docstring(module_info.docstring) if module_info.docstring else 'Module documentation.'}

"""
        
        # Add classes
        if module_info.classes:
            content += "## Classes\n\n"
            for class_info in module_info.classes:
                content += self._generate_class_section(class_info)
        
        # Add functions
        if module_info.functions:
            content += "## Functions\n\n"
            for func_info in module_info.functions:
                content += self._generate_function_section(func_info)
        
        return content
    
    def _generate_class_section(self, class_info: ClassInfo) -> str:
        """Generate documentation section for a class."""
        content = f"### {class_info.name}\n\n"
        
        # Class signature
        content += "```python\n"
        inheritance = f"({', '.join(class_info.inheritance)})" if class_info.inheritance else ""
        content += f"class {class_info.name}{inheritance}:\n"
        if class_info.docstring:
            first_line = class_info.docstring.split('\n')[0]
            content += f'    """{first_line}"""\n'
        content += "```\n\n"
        
        # Class docstring
        if class_info.docstring:
            content += f"{self._format_docstring(class_info.docstring)}\n\n"
        
        # Constructor
        if class_info.signature:
            content += "#### Constructor\n\n"
            content += "```python\n"
            content += f"def __init__({class_info.signature[1:-1]})\n"
            content += "```\n\n"
        
        # Properties
        if class_info.properties:
            content += "#### Properties\n\n"
            for prop in class_info.properties:
                content += f"##### {prop.name}\n\n"
                if prop.property_type:
                    content += f"**Type:** `{prop.property_type}`\n\n"
                if prop.docstring:
                    content += f"{self._format_docstring(prop.docstring)}\n\n"
        
        # Methods
        if class_info.methods:
            content += "#### Methods\n\n"
            for method in class_info.methods:
                content += self._generate_method_section(method, is_method=True)
        
        return content
    
    def _generate_function_section(self, func_info: FunctionInfo, is_method: bool = False) -> str:
        """Generate documentation section for a function."""
        prefix = "##### " if is_method else "### "
        content = f"{prefix}{func_info.name}\n\n"
        
        # Function signature
        content += "```python\n"
        if func_info.is_async:
            content += "async "
        if func_info.is_classmethod:
            content += "@classmethod\n"
        elif func_info.is_staticmethod:
            content += "@staticmethod\n"
        
        content += f"def {func_info.name}{func_info.signature or '()'}:\n"
        if func_info.docstring:
            first_line = func_info.docstring.split('\n')[0]
            content += f'    """{first_line}"""\n'
        content += "```\n\n"
        
        # Function docstring
        if func_info.docstring:
            content += f"{self._format_docstring(func_info.docstring)}\n\n"
        
        return content
    
    def _generate_method_section(self, method_info: FunctionInfo, is_method: bool = True) -> str:
        """Generate documentation section for a method."""
        return self._generate_function_section(method_info, is_method)
    
    def _format_docstring(self, docstring: str) -> str:
        """Format a docstring for MDX."""
        if not docstring:
            return ""
        
        # Clean up the docstring
        lines = docstring.strip().split('\n')
        formatted_lines = []
        
        in_code_block = False
        for line in lines:
            stripped = line.strip()
            
            # Handle code blocks
            if stripped.startswith('>>>') or stripped.startswith('...'):
                if not in_code_block:
                    formatted_lines.append('```python')
                    in_code_block = True
                formatted_lines.append(stripped[4:] if stripped.startswith('>>> ') else stripped[4:])
            else:
                if in_code_block:
                    formatted_lines.append('```')
                    in_code_block = False
                
                # Handle Args:, Returns:, etc.
                if stripped.startswith(('Args:', 'Arguments:', 'Parameters:')):
                    formatted_lines.append('**Arguments:**')
                elif stripped.startswith(('Returns:', 'Return:')):
                    formatted_lines.append('**Returns:**')
                elif stripped.startswith(('Raises:', 'Raise:')):
                    formatted_lines.append('**Raises:**')
                elif stripped.startswith(('Example:', 'Examples:')):
                    formatted_lines.append('**Example:**')
                else:
                    formatted_lines.append(line)
        
        if in_code_block:
            formatted_lines.append('```')
        
        return '\n'.join(formatted_lines)
    
    def _get_module_description(self, module_info: ModuleInfo) -> str:
        """Get a short description for the module."""
        if module_info.docstring:
            first_line = module_info.docstring.split('\n')[0]
            return first_line[:100] + "..." if len(first_line) > 100 else first_line
        return f"API documentation for {module_info.name}"
    
    def _categorize_modules(self, modules: Dict[str, ModuleInfo]) -> Dict[str, Dict[str, ModuleInfo]]:
        """Categorize modules for better organization."""
        categories = {
            "Authentication & Sessions": {},
            "Access Control & Detection": {},
            "Exploit Engine": {},
            "Reporting & Compliance": {},
            "Utilities": {},
            "Configuration": {},
            "Other": {}
        }
        
        for name, module in modules.items():
            if 'auth' in name:
                categories["Authentication & Sessions"][name] = module
            elif 'access' in name:
                categories["Access Control & Detection"][name] = module
            elif any(x in name for x in ['exploit', 'runner', 'async']):
                categories["Exploit Engine"][name] = module
            elif 'reporter' in name or 'reporting' in name:
                categories["Reporting & Compliance"][name] = module
            elif any(x in name for x in ['config', 'performance', 'logging']):
                categories["Configuration"][name] = module
            elif any(x in name for x in ['utils', 'cache', 'middleware']):
                categories["Utilities"][name] = module
            else:
                categories["Other"][name] = module
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


def main():
    """Main function to generate API documentation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate API documentation for LogicPwn')
    parser.add_argument('--package', default='logicpwn', help='Package to document')
    parser.add_argument('--output', default='doks/purple-atmosphere/src/content/docs/api-reference', 
                       help='Output directory')
    parser.add_argument('--clean', action='store_true', help='Clean output directory first')
    
    args = parser.parse_args()
    
    package_path = Path(args.package)
    output_dir = Path(args.output)
    
    if not package_path.exists():
        print(f"Package path does not exist: {package_path}")
        return 1
    
    if args.clean and output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
        print(f"Cleaned output directory: {output_dir}")
    
    print(f"Extracting API documentation from {package_path}...")
    extractor = APIDocumentationExtractor(str(package_path), str(output_dir))
    modules = extractor.extract_all_modules()
    
    print(f"Found {len(modules)} modules")
    for module_name in sorted(modules.keys()):
        print(f"  - {module_name}")
    
    print(f"Generating MDX files in {output_dir}...")
    generator = AstroMDXGenerator(str(output_dir))
    generator.generate_all_docs(modules)
    
    print("API documentation generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
