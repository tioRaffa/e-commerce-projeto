import random
from django.core.management.base import BaseCommand
from faker import Faker
from books.models import BookModel, AuthorModel, CategoryModel

class Command(BaseCommand):
    help = 'Creates a specified number of random books'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='The number of books to create', default=10)

    def handle(self, *args, **options):
        count = options['count']
        fake = Faker('pt_BR')

        authors = [AuthorModel.objects.create(name=fake.name()) for _ in range(count)]
        categories = [CategoryModel.objects.create(name=fake.word()) for _ in range(count)]

        for _ in range(count):
            book = BookModel.objects.create(
                title=fake.catch_phrase(),
                publisher=fake.company(),
                published_date=fake.date(),
                description=fake.text(),
                page_count=random.randint(100, 1000),
                price=random.uniform(9.99, 99.99),
                is_active=False,
                source='random',
            )
            book.authors.set(random.sample(authors, k=random.randint(1, 3)))
            book.categories.set(random.sample(categories, k=random.randint(1, 2)))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} books'))
