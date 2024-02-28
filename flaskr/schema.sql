DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS group;
DROP TABLE IF EXISTS userGroups;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT,
  image_id INTEGER,
  group_id INTEGER,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (image_id) REFERENCES images (id),
  FOREIGN KEY (group_id) REFERENCES group (id)
);

CREATE TABLE images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  data_url TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE group (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  info TEXT NOT NULL
);

-- relational tables

CREATE TABLE userGroups (
  user_id INTEGER,
  group_id INTEGER,
  PRIMARY KEY (user_id, group_id),
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (group_id) REFERENCES group (id)
);