from django.core.management.base import BaseCommand
from books.services.google_books_api import search_google_api

class Command(BaseCommand):
    help = "Search for books in the Google Books API"

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The search query for the book')

    def handle(self, *args, **options):
        query = options['query']
        try:
            results = search_google_api(query)
            if "items" in results:
                for item in results["items"]:
                    volume_info = item.get("volumeInfo", {})
                    google_id = item.get("id")
                    title = volume_info.get("title")
                    authors = ", ".join(volume_info.get("authors", ["N/A"]))
                    self.stdout.write(self.style.SUCCESS(f'ID: {google_id} | Title: {title} | Authors: {authors}'))
            else:
                self.stdout.write(self.style.WARNING('No books found.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error searching for books: {e}'))
