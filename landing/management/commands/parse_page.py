import os
import requests
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from bs4 import BeautifulSoup
import cssutils
from urllib.parse import urljoin, urlparse
from landing.models import Page, PageElement

class Command(BaseCommand):
    help = 'Parse URL and import structure into Page and PageElement models'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL to parse')

    def handle(self, *args, **options):
        url = options['url']
        self.stdout.write(f"Parsing {url}...")

        # Check STATIC_ROOT
        if not settings.STATIC_ROOT:
            raise CommandError("STATIC_ROOT is not defined in settings.py")

        # Download HTML
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        # Extract title
        title = soup.title.string.strip() if soup.title else urlparse(url).netloc
        slug = slugify(title)[:50]

        # Remove existing page by slug
        if Page.objects.filter(slug=slug).exists():
            self.stdout.write(f"Removing existing page '{slug}'...")
            page = Page.objects.get(slug=slug)
            static_dir = os.path.join(settings.STATIC_ROOT, f"page_{slug}")
            if os.path.exists(static_dir):
                import shutil
                shutil.rmtree(static_dir)
            page.elements.all().delete()
            page.delete()

        # Create new Page
        page = Page.objects.create(title=title, slug=slug, external_url=url)
        self.stdout.write(f"Created Page: {page}")

        # Create directories for static files
        static_base = os.path.join(settings.STATIC_ROOT, f"page_{page.slug}")
        os.makedirs(os.path.join(static_base, 'css'), exist_ok=True)
        os.makedirs(os.path.join(static_base, 'images'), exist_ok=True)

        # Parse CSS: download external files
        css_files = self._download_css(soup, url, static_base, page.slug)
        page.css_files = css_files
        page.save()
        self.stdout.write(f"Downloaded {len(css_files)} CSS files")

        # Parse body structure
        body = soup.body
        if not body:
            raise CommandError("No <body> found")

        # Build tree recursively
        root_elements = self._build_tree(body, page, parent=None, order=0, css_files=css_files, base_url=url,
                                         static_base=static_base)
        self.stdout.write(f"Created {len(root_elements)} root elements")

        from django.db import transaction
        transaction.on_commit(lambda: self.stdout.write(self.style.SUCCESS(f"Import complete for {url}")))

    def _download_css(self, soup, base_url, static_base, page_slug):
        """Download CSS files and return their paths"""
        css_files = []
        links = soup.find_all('link', rel='stylesheet')
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                try:
                    resp = requests.get(full_url)
                    resp.raise_for_status()
                    filename = os.path.basename(urlparse(full_url).path) or f"style_{len(css_files)}.css"
                    css_path = os.path.join(static_base, 'css', filename)
                    with open(css_path, 'wb') as f:
                        f.write(resp.content)
                    self._rewrite_css_paths(resp.text, full_url, static_base, css_path, page_slug)
                    css_files.append(f"page_{page_slug}/css/{filename}")
                    self.stdout.write(f"Saved CSS: {css_path}")
                except Exception as e:
                    self.stdout.write(f"Failed to download CSS {full_url}: {e}", self.style.WARNING)
        return css_files

    def _rewrite_css_paths(self, css_text, css_url, static_base, css_path, page_slug):
        """Rewrite URLs in CSS to local paths"""
        # Suppress cssutils warnings for CSS3 properties
        cssutils.log.setLevel('ERROR')
        self.stdout.write(f"Rewriting CSS paths in {css_path}")
        sheet = cssutils.parseString(css_text)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for prop in rule.style:
                    if prop.name in ('background', 'background-image') and 'url(' in prop.value:
                        old_url = urljoin(css_url, prop.value.replace('url(', '').replace(')', '').strip("'\""))
                        local_path = self._download_asset(old_url, static_base, 'images')
                        if local_path:
                            prop.value = f"url(/media/page_{page_slug}/{local_path})"
                            self.stdout.write(f"Replaced {old_url} with {local_path}")
        with open(css_path, 'w') as f:
            f.write(sheet.cssText.decode('utf-8'))

    def _download_asset(self, asset_url, static_base, subdir='images'):
        """Download image/CSS asset and return relative path"""
        try:
            resp = requests.get(asset_url)
            resp.raise_for_status()
            filename = os.path.basename(urlparse(asset_url).path) or f"asset_{hash(asset_url) % 1000000}.jpg"
            asset_path = os.path.join(static_base, subdir, filename)
            with open(asset_path, 'wb') as f:
                f.write(resp.content)
            self.stdout.write(f"Downloaded asset {asset_url} to {asset_path}")
            return f"{subdir}/{filename}"
        except Exception as e:
            self.stdout.write(f"Failed to download asset {asset_url}: {e}", self.style.WARNING)
            return None

    def _build_tree(self, elem, page, parent, order, css_files, base_url, static_base):
        """Recursively build PageElement tree"""
        if not elem.name:
            return []

        # Map tags to types and detect grid/card
        tag_to_type = {
            'body': 'body',
            'header': 'pageheader',
            'h1': 'header', 'h2': 'header', 'h3': 'header',
            'p': 'text', 'span': 'text',
            'img': 'image',
            'div': 'container', 'section': 'section',
            'ul': 'list', 'ol': 'list',
            'a': 'button', 'button': 'button',
        }
        classes = ' '.join(elem.get('class', [])).lower()
        children = [child for child in elem.children if child.name]
        has_header = any(child.name in ('h1', 'h2', 'h3', 'h4') for child in children)
        has_text = any(child.name == 'p' for child in children)
        if 'row' in classes or 'grid' in classes:
            el_type = 'grid'
        elif any(cls in classes for cls in ['card', 'block', 'service', 'feature']) or \
                (elem.name == 'div' and has_header and has_text):
            el_type = 'card'
        elif elem.name == 'div' and parent and parent.type == 'pageheader':
            el_type = 'container'  # Сохраняем как container для div внутри header
        else:
            el_type = tag_to_type.get(elem.name, 'container')

        # Set props
        props = {}
        if el_type == 'header':
            props['level'] = int(elem.name[1]) if elem.name in ('h1', 'h2', 'h3') else 2
        elif el_type == 'pageheader':
            style = elem.get('style', '')
            if 'background-image' in style:
                import re
                match = re.search(r'background-image:\s*url\((.*?)\)', style)
                if match:
                    bg_url = urljoin(base_url, match.group(1).strip("'\""))
                    local_path = self._download_asset(bg_url, static_base, 'images')
                    if local_path:
                        media_path = os.path.join(settings.MEDIA_ROOT, f"page_{page.slug}", "images")
                        os.makedirs(media_path, exist_ok=True)
                        media_file_path = os.path.join(media_path, os.path.basename(local_path))
                        with open(media_file_path, 'wb') as f:
                            f.write(requests.get(bg_url).content)
                        props['background_image'] = f"/media/page_{page.slug}/images/{os.path.basename(local_path)}"
        elif el_type == 'grid':
            col_count = len([child for child in children if 'col' in ' '.join(child.get('class', [])).lower()])
            props['columns'] = max(col_count, 1)
        elif el_type == 'card':
            props['layout'] = 'vertical'
        elif el_type == 'list':
            props['ordered'] = elem.name == 'ol'
            props['items'] = [{'text': li.get_text().strip()} for li in elem.find_all('li', recursive=False)]
        elif el_type == 'button' and elem.name == 'a':
            props['href'] = elem.get('href', '')

        # Content: text + inline HTML
        content = ''.join(str(child) for child in elem.contents if child.name is None or child.name in ['span', 'strong', 'em'])
        content = content.strip()

        # HTML attrs
        html_attrs = dict(elem.attrs)
        if elem.get('style'):
            html_attrs['style'] = elem.get('style')
        # Handle images
        image_file = None
        if el_type == 'image' and 'src' in html_attrs:
            src = urljoin(base_url, html_attrs['src'])
            local_path = self._download_asset(src, static_base, 'images')
            if local_path:
                try:
                    media_path = os.path.join(settings.MEDIA_ROOT, f"page_{page.slug}", "images")
                    os.makedirs(media_path, exist_ok=True)
                    media_file_path = os.path.join(media_path, os.path.basename(local_path))
                    with open(media_file_path, 'wb') as f:
                        f.write(requests.get(src).content)
                    image_file = ContentFile(open(media_file_path, 'rb').read(), name=os.path.basename(local_path))
                    html_attrs['src'] = f"/media/page_{page.slug}/images/{os.path.basename(local_path)}"
                except Exception as e:
                    self.stdout.write(f"Failed to create image file for {src}: {e}", self.style.WARNING)
                    image_file = None

        # CSS classes
        css_classes = ' '.join(html_attrs.pop('class', []))
        if el_type == 'body':
            # Пропускаем создание PageElement для body, но сохраняем классы для шаблона
            children_order = 0
            for child in elem.children:
                if child.name and child.name not in ['span', 'strong', 'em']:
                    self._build_tree(child, page, parent, children_order, css_files, base_url, static_base)
                    children_order += 1
            return [] if parent is None else []

        # Create element
        pe = PageElement.objects.create(
            page=page,
            type=el_type,
            content=content,
            props=props,
            html_attrs=html_attrs,
            css_classes=css_classes,
            image=image_file,
            parent=parent,
            order=order,
        )
        self.stdout.write(f"Created {el_type} (order={order}, parent={parent.id if parent else None})")

        # Recurse for children
        children_order = 0
        for child in elem.children:
            if child.name and child.name not in ['span', 'strong', 'em']:
                self._build_tree(child, page, pe, children_order, css_files, base_url, static_base)
                children_order += 1

        return [pe] if parent is None else []
