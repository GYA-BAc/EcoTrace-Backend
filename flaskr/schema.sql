DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS locations;

DROP TABLE IF EXISTS userGroup;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  body TEXT,
  author_id INTEGER NOT NULL,
  image_id INTEGER,
  group_id INTEGER,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (image_id) REFERENCES images (id),
  FOREIGN KEY (group_id) REFERENCES groups (id)
);

CREATE TABLE images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data_url TEXT NOT NULL,
  author_id INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  author_id INTEGER NOT NULL,
  image_id INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (image_id) REFERENCES images (id)
);

CREATE TABLE locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  latitude Decimal(8,6) NOT NULL,
  longitude Decimal(9,6) NOT NULL,
  post_id INTEGER NOT NULL,
  FOREIGN KEY (post_id) REFERENCES post (id)
);

-- relational tables

CREATE TABLE userGroup (
  user_id INTEGER,
  group_id INTEGER,
  PRIMARY KEY (user_id, group_id),
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (group_id) REFERENCES groups (id)
);