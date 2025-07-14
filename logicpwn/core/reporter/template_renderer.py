from typing import Dict, Any
import os

class TemplateRenderer:
    def __init__(self, template_dir: str = "logicpwn/templates"):
        self.template_dir = template_dir
        try:
            from jinja2 import Environment, FileSystemLoader
            self.env = Environment(loader=FileSystemLoader(self.template_dir))
        except ImportError:
            self.env = None

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        if self.env:
            template = self.env.get_template(template_name)
            return template.render(**context)
        else:
            # Fallback: simple string replacement
            path = os.path.join(self.template_dir, template_name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for k, v in context.items():
                content = content.replace(f"{{{{{k}}}}}", str(v))
            return content 