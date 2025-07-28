import re

from mkdocs.config import Config
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from solidago import __version__


def on_page_markdown(markdown: str, page: Page, config: Config, files: Files) -> str:
    # Add Solidago version in homepage
    if page.file.src_uri == "index.md":
        version_str = f'''
!!! info "Version"
    This documentation has been generated from version **{__version__}**.
'''
        markdown = re.sub(r'{{ *version *}}', version_str, markdown)
    return markdown
