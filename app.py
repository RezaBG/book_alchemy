from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from data_models import db, Author, Book
from datetime import datetime
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_fixed_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('data/library.sqlite')}"

db.init_app(app)
migrate = Migrate(app, db) # Initialize Flask-Migrate

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birthdate']
        date_of_death = request.form['date_of_death']

        # Convert date string to Python date objects
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date() if birth_date else None
        date_of_death = datetime.strptime(date_of_death, '%Y-%m-%d').date() if date_of_death else None

        # Create new Author instance and add to database
        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        flash("Author successfully added!")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')

@app.route("/api/authors", methods=['GET'])
def get_authors():
    authors = Author.query.all()
    # Convert authors to a dictionary format
    authors_list = [
        {
            "id": author.id,
            "name": author.name,
            "birth_date": author.birth_date.strftime("%Y-%m-%d") if author.birth_date else None,
            "date_of_death": author.date_of_death.strftime("%Y-%m-%d") if author.date_of_death else None
        }
        for author in authors
    ]
    return {"authors": authors_list}, 200

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all() # Get all authors for the dropdown

    if request.method == 'POST':
        # print the form data to verify inputs
        print(request.form)
        title = request.form['title']
        isbn = request.form['isbn']
        publication_year = request.form['publication_year']
        author_id = request.form['author'] # Author ID from the dropdown

        if not author_id:
            flash("Please select a valid author")
            return redirect(url_for('add_book'))

        # Convert publication year if it's an integer
        publication_year = int(publication_year) if publication_year.isdigit() else None

        # Create new Book instance and add to database
        new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)

        try:
            db.session.commit()
            flash("Book successfully added!")
        except Exception as e:
            db.session.rollback()
            flash("An error occured while adding book")
            print(f"Error: {e}")

        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route("/api/books", methods=['GET'])
def get_books():
    books = Book.query.all()
    # Convert books to a dictionary format
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "publication_year": book.publication_year,
            "author_id": book.author_id,
            "author_name": book.author.name if book.author else None,
        }
        for book in books
    ]
    return {"books": books_list}, 200

@app.route("/book/<int:book_id>/delete", methods=['POST'])
def delete_book(book_id):
    # Proceed with the deletion logic for POST request
    book = Book.query.get(book_id)
    if book:
        # Store author ID before deleting the book
        author_id = book.author_id
        # Delete the book from the database
        db.session.delete(book)
        db.session.commit()

        # Check if the author has other books
        remaining_books = Book.query.filter_by(author_id=author_id).count()
        if remaining_books == 0:
            # If no other books by this author, delete the author
            author = Author.query.get(author_id)
            if author:
                db.session.delete(author)
                db.session.commit()

            flash("Book successfully deleted")
        else:
            flash("Book not found.")
        # Redirect to home after deletion
        return redirect(url_for('home'))


@app.route("/")
def home():
    search_term = request.args.get("search")
    if search_term:
        # Filter books based on the search term
        books = Book.query.filter(Book.title.ilike(f"%{search_term}%")).all()
    else:
        books = Book.query.all() # Get all books if no search term
    return render_template('home.html', books=books)

if __name__ == "__main__":
    app.run(debug=True)
