from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return '<Author: {}>'.format(self.name)

    def __str__(self):
        return '<Author: {}>'.format(self.name)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.String, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return '<Book: {}>'.format(self.title)

    def __str__(self):
        return '<Book: {}>'.format(self.title)

