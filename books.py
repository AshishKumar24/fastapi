from fastapi import FastAPI
from schemas import read_data, get_book_by_isbn, Books
import uvicorn

app = FastAPI()

data = read_data()


@app.get("/")
def main():
    return {
        "message": f"Hello World"
    }


@app.get("/books")
def get_all_books():
    return {
        "message": data
    }


@app.get("/books/{isbn}")
def get_book(isbn):
    return get_book_by_isbn(isbn)


@app.post("/books")
def insert_book(book: Books):
    return {'message': book}


if __name__ == "__main__":
    uvicorn.run("books:app", reload=True)
