-- Таблица пользователей
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Общие слова (для всех)
CREATE TABLE common_words (
    id SERIAL PRIMARY KEY,
    word_rus VARCHAR(100) NOT NULL,
    word_eng VARCHAR(100) NOT NULL
);

-- Пользовательские слова
CREATE TABLE user_words (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    word_rus VARCHAR(100) NOT NULL,
    word_eng VARCHAR(100) NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);