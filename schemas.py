from pydantic import BaseModel
import json


class Books(BaseModel):
    title: str
    isbn: str
    pageCount: int
    thumbnailUrl: str
    status: str
    authors: list
    categories: list


def read_data():
    with open('books.json') as f:
        json_data = json.loads(f.read())

    return json_data


def get_book_by_isbn(isbn):
    for i in read_data():
        if 'isbn' in i:
            if i['isbn'] == isbn:
                return isbn
    return {f'No books with {isbn}'}
