CREATE DATABASE motion DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;

USE motion;

CREATE TABLE IF NOT EXISTS events (
  file varchar(200) COLLATE utf8_bin NOT NULL,
  location varchar(50) COLLATE utf8_bin NOT NULL,
  size int(11) DEFAULT NULL,
  diff_cnt int(11) DEFAULT NULL,
  time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  url varchar(500) COLLATE utf8_bin DEFAULT NULL,
  uploaded timestamp NULL DEFAULT NULL,
  PRIMARY KEY (file)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE USER 'picam'@'localhost';

GRANT ALL ON motion.* TO 'picam'@'localhost';
