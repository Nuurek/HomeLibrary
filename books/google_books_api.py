from django.utils.html import strip_tags
from googleapiclient import discovery
from googleapiclient.http import HttpRequest
import urllib.request
import urllib.parse
import json
from django.conf import settings
from httplib2 import Http
from typing import List

from .models import Book


class GoogleBooksAPI(object):

    def __init__(self):
        self.url = 'https://www.googleapis.com/books/v1/volumes'

    def search(self, query: str):
        query = query.strip()
        if len(query) == 0:
            return []
        query = query.replace(' ', '+')

        parameters = urllib.parse.urlencode({
            'q': query,
            'printType': 'books',
            'projection': 'full',
            'maxResults': '20',
            'key': settings.GOOGLE_BOOKS_API_KEY,
        })
        request = urllib.request.Request(self.url + '?' + parameters)
        response = urllib.request.urlopen(request)
        data = json.load(response)

        books = data['items']
        books = [self.api_response_to_tag_dict(book) for book in books]
        books = [book for book in books if book is not None]
        books = self.filter_existing_books(books)

        return books

    def get(self, volume_id):
        request = urllib.request.Request(self.url + '/' + volume_id)
        response = urllib.request.urlopen(request)
        data = json.load(response)
        return self.api_response_to_tag_dict(data)

    @staticmethod
    def api_response_to_tag_dict(api_book):
        book = dict()
        book['id'] = api_book['id']
        volume_info: dict = api_book['volumeInfo']

        try:
            book['title'] = volume_info['title']
            if 'subtitle' in volume_info:
                book['title'] += '. ' + volume_info['subtitle']
            book['author'] = volume_info['authors'][0]
            description = strip_tags(volume_info['description'])[0:Book._meta.get_field('description').max_length - 1]
            book['description'] = description
            book['page_count'] = volume_info['pageCount']
            book['cover'] = dict()
            book['cover']['url'] = '&'.join([volume_info['imageLinks']['thumbnail'].split('&')[0],
                                      'printsec=frontcover', 'img=1', 'zoom=2'])
        except KeyError:
            return None

        return book

    @staticmethod
    def filter_existing_books(books: List[dict]):
        filtered_books = []
        for book in books:
            try:
                Book.objects.get(title=book['title'], author=book['author'])
            except Book.DoesNotExist:
                filtered_books.append(book)

        return filtered_books
