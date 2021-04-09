#!/usr/bin/env python


from typing import Optional
import logging
import sqlite3


class DBManager:
    db_file_name = "song_video.db"
    table_name = "song_video"


    def __init__(self, logger: logging.Logger, db_file_name: str, table_name: str) -> None:
        self.logger = logger
        self.db_file_name = db_file_name
        self.table_name = table_name
        self.conn = sqlite3.connect(self.db_file_name)


    def __del__(self) -> None:
        self.conn.close()


    def get_video_id_by_song_name(self, song_name: str) -> Optional[str]:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT video_id FROM %s WHERE song_name = '%s'" % (self.table_name, song_name))
            row = cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(e)

        if not row:
            return None
        return row[0]


    def get_random_video_id_by_year(self, year: int) -> Optional[str]:
        print("# get_random_video_id_by_year(year=%d)" % year)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT video_id FROM %s WHERE year = %d ORDER BY RANDOM() LIMIT 1" % (self.table_name, year))
            row = cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(e)

        if not row:
            return None
        return row[0]


    def get_random_video_id(self) -> Optional[str]:
        print("# get_random_video_id()")
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT video_id FROM %s ORDER BY RANDOM() LIMIT 1" % self.table_name)
            row = cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(e)

        if not row:
            return None
        return row[0]


    def put(self, song_name: str, year: int, video_id: Optional[str], video_name: Optional[str]) -> None:
        if not video_id:
            video_id = ""
        if not video_name:
            video_name = ""
        try:
            self.conn.execute("INSERT OR REPLACE INTO %s (song_name, year, video_id, video_name) VALUES ('%s', %d, '%s', '%s')" % (self.table_name, song_name, year, video_id, video_name))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(e)

