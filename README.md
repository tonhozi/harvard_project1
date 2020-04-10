# Project 1

Web Programming with Python and JavaScript

## Notes about the code

User is able to login and logout as requested. Menu is updated if the user is logged or not. I kept it simple and limited to the scope of the project guidelines.

Once logged, they can do a search on the top bar. This search is stored and does not erase unless the user makes a new search. I added a pagination to the search results.

List all books does exactly what it says.

Once the user pick a book, they can click on more info. This will take to the book page.

In the book page, the user will see a cover of the book, the required data from the API and DB, a field for a review and the review from other members. I implemented add a review, but not edit or delete (as it was not in the scope of the project nor implied as needed).

Finally, after submiting a review, the page updates itself and display the new review. It also shows the submitted review instead of the form, blocking this way the user to submit a new review. Just in case they are snicky, I have also created a check in the backend to block a post request for a user that already has a review.

I added the import code and also a book API (/api/<string:isbn>) line 221 of the application.py.

## Tables created

```SQL
CREATE TABLE books (
      id SERIAL PRIMARY KEY,
      title VARCHAR(255) NOT NULL,
      author VARCHAR(255) NOT NULL,
      isbn VARCHAR(10) NOT NULL,
      year INTEGER NOT NULL
  );
```

```SQL
CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      username VARCHAR NOT NULL,
      psw_hash VARCHAR NOT NULL,
      nickname VARCHAR NOT NULL,
  );
```

```SQL
CREATE TABLE review (
      id SERIAL PRIMARY KEY,
      title VARCHAR NOT NULL,
      detail VARCHAR NOT NULL,
      rating INTEGER NOT NULL,
      user_id INTEGER REFERENCES users,
      book_id INTEGER REFERENCES books,
  );
```

## ENV settings

export DATABASE_URL="" # Set environment link to postgreSQL database
export FLASK_DEBUG=1
export FLASK_APP=application.py
export GOODREADS_API= # Set api for goodreads

## Requirements for the project

- [x] Registration: Users should be able to register for your website, providing (at minimum) a username and password.
- [x] Login: Users, once registered, should be able to log in to your website with their username and password.
- [x] Logout: Logged in users should be able to log out of the site.
- [x] Import: Provided for you in this project is a file called books.csv, which is a spreadsheet in CSV format of 5000 different books. Each one has an ISBN number, a title, an author, and a publication year. In a Python file called import.py separate from your web application, write a program that will take the books and import them into your PostgreSQL database. You will first need to decide what table(s) to create, what columns those tables should have, and how they should relate to one another. Run this program by running python3 import.py to import the books into your database, and submit this program with the rest of your project code.
- [x] Search: Once a user has logged in, they should be taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, your website should display a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, your search page should find matches for those as well!
- [x] Book Page: When users click on a book from the results of the search page, they should be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on your website.
- [x] Review Submission: On the book page, users should be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users should not be able to submit multiple reviews for the same book.
- [x] Goodreads Review Data: On your book page, you should also display (if available) the average rating and number of ratings the work has received from Goodreads.
- [x] API Access: If users make a GET request to your website’s /api/<isbn> route, where <isbn> is an ISBN number, your website should return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. The resulting JSON should follow the format:
      {
      "title": "Memory",
      "author": "Doug Lloyd",
      "year": 2015,
      "isbn": "1632168146",
      "review_count": 28,
      "average_score": 5.0
      }
      If the requested ISBN number isn’t in your database, your website should return a 404 error.

- [x] In README.md, include a short writeup describing your project, what’s contained in each file, and (optionally) any other additional information the staff should know about your project.
- [x] If you’ve added any Python packages that need to be installed in order to run your web application, be sure to add them to requirements.txt!
