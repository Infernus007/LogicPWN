# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

master_doc = 'index'

project = 'LogicPwn'
copyright = '2024, LogicPwn Team'
author = 'LogicPwn Team'
release = '0.1.0'

# Enhanced metadata for SEO
html_title = "LogicPwn - Advanced Business Logic Security Testing Framework"
html_short_title = "LogicPwn Docs"

# SEO and meta information
html_meta = {
    'description': 'LogicPwn is the most advanced open-source business logic security testing framework for penetration testing, bug bounty hunting, and automated vulnerability assessment.',
    'keywords': 'security testing, business logic vulnerabilities, IDOR testing, penetration testing, bug bounty, vulnerability assessment, automated security, Python security framework, exploit chaining, access control testing',
    'author': 'LogicPwn Development Team',
    'robots': 'index, follow',
    'viewport': 'width=device-width, initial-scale=1.0',
    'og:title': 'LogicPwn - Advanced Business Logic Security Testing Framework',
    'og:description': 'The only open-source framework specifically designed for business logic exploitation and multi-step attack automation.',
    'og:type': 'website',
    'og:url': 'https://logicpwn.readthedocs.io/',
    'og:image': 'https://logicpwn.readthedocs.io/_static/logicpwn-logo.png',
    'twitter:card': 'summary_large_image',
    'twitter:title': 'LogicPwn - Advanced Business Logic Security Testing Framework',
    'twitter:description': 'Discover business logic vulnerabilities that traditional scanners miss with LogicPwn.',
}

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
    'analytics_id': '',  # Add your Google Analytics ID here
}

# Favicon
html_favicon = '_static/favicon.svg'

# Logo
html_logo = '_static/logicpwn-logo-v2.svg'

# Show "Edit on GitHub" links
html_context = {
    'display_github': True,
    'github_user': 'logicpwn',
    'github_repo': 'logicpwn',
    'github_version': 'main',
    'conf_py_path': '/docs/source/',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS for better styling
html_css_files = [
    'custom.css',
]

# Custom HTML head content for SEO and branding
html_extra_head = """
    <!-- Additional SEO -->
    <link rel="sitemap" type="application/xml" href="_static/sitemap.xml">
    
    <!-- Schema.org structured data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "LogicPWN",
        "description": "Advanced business logic vulnerability testing framework for penetration testers, bug bounty hunters, and security teams.",
        "url": "https://logicpwn.readthedocs.io/",
        "applicationCategory": "SecurityApplication",
        "operatingSystem": "Cross-platform",
        "programmingLanguage": "Python",
        "license": "https://opensource.org/licenses/MIT",
        "author": {
            "@type": "Organization",
            "name": "LogicPWN Team"
        },
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }
    }
    </script>
"""

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'LogicPwndoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'LogicPwn.tex', 'LogicPwn Documentation',
     'LogicPwn Team', 'manual'),
]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'logicpwn', 'LogicPwn Documentation',
     [author], 1)
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'LogicPwn', 'LogicPwn Documentation',
     author, 'LogicPwn', 'Business Logic Exploitation & Exploit Chaining Automation Tool',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Napoleon settings for Google/NumPy docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
    # 'pydantic': ('https://docs.pydantic.dev/', None),
}

# Todo settings
todo_include_todos = True

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Custom settings for LogicPwn -------------------------------------------

# Add custom CSS for better styling
def setup(app):
    app.add_css_file('custom.css')
