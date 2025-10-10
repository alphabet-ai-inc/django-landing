from django.core.management.base import BaseCommand, CommandError
from landing.services.page_parser import PageParserService


class Command(BaseCommand):
    help = 'Parse URL and import structure into Page and PageElement models'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL to parse')

    def handle(self, *args, **options):
        url = options['url']
        self.stdout.write(f"Parsing {url}...")

        try:
            parser = PageParserService(url)
            page = parser.parse_and_import()
            self.stdout.write(self.style.SUCCESS(f"Successfully imported page: {page.title} ({page.slug})"))
        except Exception as e:
            raise CommandError(f"Failed to parse page: {e}")
