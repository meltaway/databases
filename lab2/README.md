# Створення додатку бази даних, орієнтованого на взаємодію з СУБД PostgreSQL

## News
|name|data type|not null|PK|FK|
|--|--|--|--|--|
|id|integer|yes|yes
|date|date|yes|no
|title|text|yes|no
|category|text|yes|no
|description|text|yes|no
|rating|float|yes|no

## Tags
|name|data type|not null|PK|FK|
|--|--|--|--|--|
|id|integer|yes|yes
|name|text|yes|no

## Topics
|name|data type|not null|PK|FK|
|--|--|--|--|--|
|id|integer|yes|yes
|name|text|yes|no

## News Tags
|name|data type|not null|PK|FK|
|--|--|--|--|--|
|id|integer|yes|yes
|tag_id|integer|yes|no|tags.id
|news_id|integer|yes|no|news.id

## Tag Topics
|name|data type|not null|PK|FK|
|--|--|--|--|--|
|id|integer|yes|yes
|topic_id|integer|yes|no|topics.id
|tag_id|integer|yes|no|tags.id

## Database Diagram
![DB Diagram](./docs/diag.png)