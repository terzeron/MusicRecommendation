#!/bin/sh

(
echo "CREATE TABLE song_video (song_name varchar(1024) not null, year int not null, video_id varchar(13) null, video_name varchar(4096) null, constraint song_video_pk primary key (song_name));" 
echo "CREATE INDEX song_video_idx_year ON song_video (year);"
) | sqlite3 song_video.db
