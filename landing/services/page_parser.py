"""
Service for parsing web pages and importing them into the database.
"""
import os
import shutil
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from bs4 import BeautifulSoup, Comment
import cssutils
from urllib.parse import urljoin, urlparse
from landing.models import Page, PageElement


class CSSProcessor:
    """Handles CSS file downloading and URL rewriting."""

    def __init__(self, base_url, static_base, page_slug):
        self.base_url = base_url
        self.static_base = static_base
        self.page_slug = page_slug
        cssutils.log.setLevel('ERROR')  # Suppress warnings
        self.base_domain = urlparse(base_url).netloc

    def download_css_files(self, soup):
        """Download CSS files from the page or keep external URLs."""
        css_files = []
        links = soup.find_all('link', rel='stylesheet')

        for link in links:
            href = link.get('href')
            if not href:
                continue

            full_url = urljoin(self.base_url, href)
            url_domain = urlparse(full_url).netloc

            if url_domain and url_domain != self.base_domain:
                css_files.append(full_url)
                continue

            try:
                resp = requests.get(full_url, timeout=10)
                resp.raise_for_status()

                filename = os.path.basename(urlparse(full_url).path) or f"style_{len(css_files)}.css"
                css_path = os.path.join(self.static_base, 'css', filename)

                # Переписываем URLs и сохраняем изменённый CSS
                sheet = self._rewrite_css_urls(resp.text, full_url, css_path)
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(sheet.cssText.decode('utf-8'))  # Сохраняем изменённый CSS

                css_files.append(f"page_{self.page_slug}/css/{filename}")

            except Exception as e:
                print(f"Failed to download CSS {full_url}: {e}")

        return css_files

    def _rewrite_css_urls(self, css_text, css_url, css_path):
        """Rewrite URLs in CSS to local paths in MEDIA_ROOT and return modified sheet."""
        sheet = cssutils.parseString(css_text)

        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for prop in rule.style:
                    if prop.name in ('background', 'background-image') and 'url(' in prop.value:
                        old_url = prop.value.replace('url(', '').replace(')', '').strip("'\"")
                        full_asset_url = urljoin(css_url, old_url)

                        # Скачиваем изображение в MEDIA_ROOT
                        image_file = AssetDownloader.download_to_media(full_asset_url, self.page_slug, 'images')
                        if image_file:
                            relative_path = f"images/{image_file.name}"
                            prop.value = f"url(/media/page_{self.page_slug}/{relative_path})"
                            print(f"Rewrote URL to: url(/media/page_{self.page_slug}/{relative_path})")

        return sheet  # Возвращаем изменённый sheet


class AssetDownloader:
    """Handles downloading of images and other assets."""

    @staticmethod
    def download_asset(asset_url, static_base, subdir='images'):
        """Download an asset and return its relative path."""
        try:
            resp = requests.get(asset_url, timeout=10)
            resp.raise_for_status()

            filename = os.path.basename(urlparse(asset_url).path)
            if not filename:
                filename = f"asset_{hash(asset_url) % 1000000}.jpg"

            asset_path = os.path.join(static_base, subdir, filename)

            with open(asset_path, 'wb') as f:
                f.write(resp.content)

            return f"{subdir}/{filename}"

        except Exception as e:
            print(f"Failed to download asset {asset_url}: {e}")
            return None

    @staticmethod
    def download_to_media(asset_url, page_slug, subdir='images'):
        """Download asset directly to MEDIA_ROOT."""
        try:
            resp = requests.get(asset_url, timeout=10)
            resp.raise_for_status()

            filename = os.path.basename(urlparse(asset_url).path)
            if not filename:
                filename = f"asset_{hash(asset_url) % 1000000}.jpg"

            media_path = os.path.join(settings.MEDIA_ROOT, f"page_{page_slug}", subdir)
            os.makedirs(media_path, exist_ok=True)

            media_file_path = os.path.join(media_path, filename)
            with open(media_file_path, 'wb') as f:
                f.write(resp.content)

            return ContentFile(resp.content, name=filename)

        except Exception as e:
            print(f"Failed to download to media {asset_url}: {e}")
            return None


class ElementTreeBuilder:
    """Builds PageElement tree from HTML structure."""

    TAG_TO_TYPE = {
        'body': 'body',
        'header': 'pageheader',
        'legend': 'legend',
        'form': 'form',
        'label': 'label',
        'input': 'input',
        'textarea': 'textarea',
        'h1': 'header', 'h2': 'header', 'h3': 'header', 'h4': 'header',
        'p': 'text', 'span': 'text',
        'img': 'image',
        'div': 'container', 'section': 'section',
        'ul': 'list', 'ol': 'list',
        'li': 'list_item',
        'a': 'button', 'button': 'button',
    }

    def __init__(self, page, base_url, static_base):
        self.page = page
        self.base_url = base_url
        self.static_base = static_base

    def build_tree(self, elem, parent=None, order=0):
        """Recursively build PageElement tree."""
        if not elem.name:
            return []

        el_type = self._determine_element_type(elem, parent)

        if el_type == 'body':
            return self._process_body(elem, parent)

        props = self._extract_props(elem, el_type)
        content = self._extract_content(elem)
        html_attrs = dict(elem.attrs)
        css_classes = ' '.join(html_attrs.pop('class', []))

        image_file = self._process_image(elem, el_type, html_attrs)

        # Create element
        pe = PageElement.objects.create(
            page=self.page,
            type=el_type,
            content=content,
            props=props,
            html_attrs=html_attrs,
            css_classes=css_classes,
            image=image_file,
            parent=parent,
            order=order,
        )

        # Process children
        self._process_children(elem, pe)

        return [pe] if parent is None else []

    def _determine_element_type(self, elem, parent):
        """Determine the element type based on tag and classes."""
        classes = ' '.join(elem.get('class', [])).lower()
        children = [child for child in elem.children if child.name]

        has_header = any(child.name in ('h1', 'h2', 'h3', 'h4') for child in children)
        has_text = any(child.name == 'p' for child in children)

        if 'row' in classes or 'grid' in classes:
            return 'grid'
        elif any(cls in classes for cls in ['card', 'block', 'service', 'feature']) or \
                (elem.name == 'div' and has_header and has_text):
            return 'card'
        elif elem.name == 'div' and parent and parent.type == 'pageheader':
            return 'container'

        return self.TAG_TO_TYPE.get(elem.name, 'container')

    def _extract_props(self, elem, el_type):
        """Extract properties based on element type."""
        props = {}

        if el_type == 'header':
            props['level'] = int(elem.name[1]) if elem.name in ('h1', 'h2', 'h3', 'h4') else 2

        elif el_type == 'pageheader':
            props = self._extract_header_background(elem)

        elif el_type == 'form':
            props['action'] = elem.get('action', '')
            props['method'] = elem.get('method', 'get').upper()

        elif el_type == 'label':
            props['for'] = elem.get('for', '')

        elif el_type == 'input':
            props['type'] = elem.get('type', 'text')
            props['id'] = elem.get('id', '')
            props['name'] = elem.get('name', '')

        elif el_type == 'textarea':
            props['id'] = elem.get('id', '')
            props['name'] = elem.get('name', '')

        elif el_type == 'grid':
            children = [child for child in elem.children if child.name]
            col_count = len([child for child in children if 'col' in ' '.join(child.get('class', [])).lower()])
            props['columns'] = max(col_count, 1)

        elif el_type == 'card':
            props['layout'] = 'vertical'

        elif el_type == 'list':
            props['ordered'] = elem.name == 'ol'

        elif el_type == 'button' and elem.name == 'a':
            props['href'] = elem.get('href', '')

        return props

    def _extract_header_background(self, elem):
        """Extract background image from header style."""
        props = {}
        style = elem.get('style', '')

        if 'background-image' in style:
            import re
            match = re.search(r'background-image:\s*url\((.*?)\)', style)
            if match:
                bg_url = urljoin(self.base_url, match.group(1).strip("'\""))
                image_file = AssetDownloader.download_to_media(bg_url, self.page.slug, 'images')
                if image_file:
                    props['background_image'] = f"/media/page_{self.page.slug}/images/{image_file.name}"

        return props

    def _extract_content(self, elem):
        """Extract text content from element."""
        content = ''.join(
            str(child)
            for child in elem.contents
            if child.name is None and not isinstance(child, Comment)
            or child.name in ['span', 'strong', 'em', 'b', 'input']
        )
        return content.strip()

    def _process_image(self, elem, el_type, html_attrs):
        """Process image element and download file."""
        if el_type != 'image' or 'src' not in html_attrs:
            return None

        src = urljoin(self.base_url, html_attrs['src'])
        image_file = AssetDownloader.download_to_media(src, self.page.slug, 'images')

        if image_file:
            html_attrs['src'] = f"/media/page_{self.page.slug}/images/{image_file.name}"

        return image_file

    def _process_body(self, elem, parent):
        """Process body element (skip creating PageElement for body)."""
        children_order = 0
        for child in elem.children:
            if child.name and child.name not in ['span', 'strong', 'em', 'b', 'input']:
                self.build_tree(child, parent, children_order)
                children_order += 1
        return []

    def _process_children(self, elem, parent_element):
        """Process child elements recursively."""
        children_order = 0
        for child in elem.children:
            if child.name and child.name not in ['span', 'strong', 'em', 'b', 'input']:
                self.build_tree(child, parent_element, children_order)
                children_order += 1


class PageParserService:
    """Main service for parsing and importing web pages."""

    def __init__(self, url):
        self.url = url
        self.page = None
        self.static_base = None

    def parse_and_import(self):
        """Parse URL and import into database."""
        if not settings.STATIC_ROOT:
            raise ValueError("STATIC_ROOT is not defined in settings.py")

        # Download HTML
        response = requests.get(self.url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        # Create or update page
        title, slug = self._extract_page_info(soup)
        self._cleanup_existing_page(slug)
        self.page = Page.objects.create(title=title, slug=slug, external_url=self.url)

        # Setup directories
        self._setup_static_directories()

        # Process CSS
        css_processor = CSSProcessor(self.url, self.static_base, self.page.slug)
        css_files = css_processor.download_css_files(soup)
        self.page.css_files = css_files
        self.page.save()

        # Build element tree
        body = soup.body
        if not body:
            raise ValueError("No <body> found in HTML")

        tree_builder = ElementTreeBuilder(self.page, self.url, self.static_base)
        tree_builder.build_tree(body)

        return self.page

    def _extract_page_info(self, soup):
        """Extract title and generate slug."""
        title = soup.title.string.strip() if soup.title else urlparse(self.url).netloc
        slug = slugify(title)[:50]
        return title, slug

    def _cleanup_existing_page(self, slug):
        """Remove existing page and its static files."""
        if Page.objects.filter(slug=slug).exists():
            page = Page.objects.get(slug=slug)
            static_dir = os.path.join(settings.STATIC_ROOT, f"page_{slug}")

            if os.path.exists(static_dir):
                shutil.rmtree(static_dir)

            page.elements.all().delete()
            page.delete()

    def _setup_static_directories(self):
        """Create directories for static files."""
        self.static_base = os.path.join(settings.STATIC_ROOT, f"page_{self.page.slug}")
        os.makedirs(os.path.join(self.static_base, 'css'), exist_ok=True)
        os.makedirs(os.path.join(self.static_base, 'images'), exist_ok=True)
