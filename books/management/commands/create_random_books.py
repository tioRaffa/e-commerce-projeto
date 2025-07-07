import random
from django.core.management.base import BaseCommand
from books.models import BookModel
from books.services.google_books_api import search_google_api, import_from_google_api

class Command(BaseCommand):
    help = 'Creates a specified number of random books'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, help='The number of random books to create from Google Books.', default=None)
        parser.add_argument('--title', type=str, help='The specific title of the book to import from Google Books.', default=None)

    def handle(self, *args, **options):
        count = options['count']
        title = options['title']

        if count is not None and title is not None:
            self.stdout.write(self.style.ERROR('Please provide either --count or --title, not both.'))
            return

        if count is None and title is None:
            self.stdout.write(self.style.ERROR('Please provide either --count or --title.'))
            return

        if count is not None:
            self._import_random_books(count)
        elif title is not None:
            self._import_specific_book(title)

    def _import_random_books(self, count):
        self.stdout.write(self.style.SUCCESS(f'Importing {count} random books from Google Books...'))
        queries = ["fiction", "science", "history", "biography", "fantasy", "thriller", "romance", "mystery", "horror", "poetry"]
        imported_count = 0
        for _ in range(count):
            query = random.choice(queries)
            try:
                response = search_google_api(query)
                items = response.get('items', [])
                if not items:
                    self.stdout.write(self.style.WARNING(f'No books found for query: {query}. Trying another query.'))
                    continue

                # Pick a random book from the search results
                item = random.choice(items)
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

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred during random book import: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Finished importing {imported_count} random books.'))

    def _import_specific_book(self, title):
        self.stdout.write(self.style.SUCCESS(f'Searching for specific book: {title}'))
        try:
            response = search_google_api(title)
            items = response.get('items', [])

            if not items:
                self.stdout.write(self.style.WARNING(f'No book found with title: {title}'))
                return

            # Try to find an exact match or the closest one
            found_book = None
            for item in items:
                if item.get('volumeInfo', {}).get('title', '').lower() == title.lower():
                    found_book = item
                    break
            if not found_book and items:
                found_book = items[0] # Take the first result if no exact match

            if found_book:
                google_books_id = found_book['id']
                try:
                    book = import_from_google_api(google_books_id)
                    book.stock = random.randint(1, 100)  # Ensure stock is at least 1
                    book.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported: {book.title}'))
                except ValueError as e:
                    self.stdout.write(self.style.WARNING(f'Skipping book (already exists or invalid): {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing book {google_books_id}: {e}'))
            else:
                self.stdout.write(self.style.WARNING(f'Could not find a suitable book for title: {title}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during specific book import: {e}'))
