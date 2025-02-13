from datetime import datetime
from sqlite3.dbapi2 import DatabaseError
from database_connection import database_connection as default_database_connection
from services.reading_tip_factory import ReadingTipFactory
# pylint: disable=missing-function-docstring


def give_tip_object(row):
    """A helper function for creating tip objects from row objects."""
    tip = ReadingTipFactory.get_new_reading_tip(row["type"])
    tip.set_values_from_dict(row)
    return tip


class TipsRepository:
    """Class for making SQL quaries dealing with reading tips.
    """

    def __init__(self, database_connection=default_database_connection):
        self._connection = database_connection

    def get_tips(self):
        sql = "SELECT * FROM Tips WHERE visible=TRUE;"
        cursor = self._connection.cursor()
        tips = cursor.execute(sql).fetchall()

        return list(map(give_tip_object, tips))

    def remove_tip(self, tip_id):
        try:
            sql = "UPDATE Tips SET visible=FALSE WHERE id=? AND visible=TRUE;"
            cursor = self._connection.cursor()
            cursor.execute(sql, [tip_id])
            self._connection.commit()
            if cursor.rowcount == 1:
                return True
            return False
        except DatabaseError:
            return False

    def store_reading_tip(self, tip):
        try:
            cursor = self._connection.cursor()
            contents = tip.get_contents()
            if not "tip_id" in contents:
                sql = """INSERT INTO Tips (type, title, datetime, visible)
                         VALUES (?, ?, ?, TRUE)"""
                cursor.execute(
                    sql, [contents["type"], contents["title"], datetime.now()])
                self._connection.commit()
                tip.tip_id = cursor.lastrowid
                return True

            sql = """UPDATE Tips SET title=:title
                        WHERE id=? AND visible=TRUE"""
            cursor.execute(sql, [contents["tip_id"]])
            self._connection.commit()
            if cursor.rowcount == 1:
                return True
            return False
        except DatabaseError:
            return False


tips_repository = TipsRepository()
