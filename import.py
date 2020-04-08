import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    num_lines = sum(1 for line in open("books.csv")) - 1
    with open("books.csv", "r") as csvfile:
        csvReader = csv.reader(csvfile)
        next(csvReader)
        for isbn, title, author, year in csvReader:

            db.execute(
                "INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {"isbn": isbn, "title": title, "author": author, "year": year},
            )
            current_line = csvReader.line_num - 1
            print(
                f"{current_line}/{num_lines}\tAdded book: ISBN {isbn}\t{title} ({author}/{year})."
            )
        db.commit()


if __name__ == "__main__":
    main()
