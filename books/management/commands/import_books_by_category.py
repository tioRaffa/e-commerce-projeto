import random
from django.core.management.base import BaseCommand
from books.models import BookModel
from books.services.google_books_api import search_google_api, import_from_google_api

class Command(BaseCommand):
    help = 'Imports random books from Google Books based on a category name.'

    def add_arguments(self, parser):
        parser.add_argument('category_name', type=str, help='The category name to search for on Google Books.')

    def handle(self, *args, **options):
        category_name = options['category_name']
        self.stdout.write(self.style.SUCCESS(f'Searching Google Books for books in category: {category_name}'))

        try:
            response = search_google_api(category_name)
            items = response.get('items', [])

            if not items:
                self.stdout.write(self.style.WARNING(f'No books found for category: {category_name}'))
                return

            imported_count = 0
            for item in items:
                if imported_count >= 5:
                    self.stdout.write(self.style.WARNING('Reached the limit of 5 imported books.'))
                    break
                google_books_id = item['id']
                try:
                    book = import_from_google_api(google_books_id)
                    book.stock = random.randint(1, 100)  # Ensure stock is at least 1
                    book.save()
                    imported_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported: {book.title}'))
                except ValueError as e:
                    self.stdout.write(self.style.WARNING(f'Skipping book (already exists or invalid): {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing book {google_books_id}: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Finished importing {imported_count} books for category: {category_name}.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))