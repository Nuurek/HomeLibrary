from googleapiclient import discovery
from googleapiclient.http import HttpRequest
from httplib2 import Http


class GoogleBooksAPI:
    api = discovery.build('books', 'v1')

    def search(self, query: str):
        query = query.strip()
        if len(query) == 0:
            return []
        query = query.replace(' ', '+')

        http = Http()
        request: HttpRequest = GoogleBooksAPI.api.volumes().list(
            q=query, printType='books', projection='full', maxResults=20
        )
        response = request.execute(http=http)

        books = response['items']
        books = [self.api_response_to_tag_dict(book) for book in books]
        books = [book for book in books if book is not None]

        return books

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
            book['description'] = volume_info['description']
            book['page_count'] = volume_info['pageCount']
            book['cover'] = '&'.join(volume_info['imageLinks']['thumbnail'].split('&')[0:-3] + ['zoom=2'])

            pdf_info = api_book['accessInfo']['pdf']
            if pdf_info['isAvailable'] and 'downloadLink' in pdf_info:
                book['ebook_link'] = pdf_info['downloadLink']
        except KeyError:
            return None

        return book
