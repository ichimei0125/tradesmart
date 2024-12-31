CREATE DATABASE tradedb;

CREATE USER 'tradebot'@'localhost' IDENTIFIED BY '{your_password}';

GRANT ALL PRIVILEGES ON tradedb.* TO 'tradebot'@'localhost';

FLUSH PRIVILEGES;