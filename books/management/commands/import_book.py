from django.core.management.base import BaseCommand
from books.services.google_books_api import import_from_google_api

class Command(BaseCommand):
    help = "Import a book from the Google Books API by its ID"

    def add_arguments(self, parser):
        parser.add_argument('google_id', type=str, help='The Google Books ID of the book to import')

    def handle(self, *args, **options):
        google_id = options['google_id']
        try:
            book = import_from_google_api(google_id)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported book: {book.title}'))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'Error importing book: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
