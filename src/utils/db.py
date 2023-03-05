import os
import sqlalchemy
from flask import g
from sqlalchemy import text
from werkzeug.exceptions import abort

DATABASE = os.environ.get("DATABASE")
DATABASE_USER_NAME = os.environ.get("DATABASE_USER_NAME")
DATABASE_USER_PASSWORD = os.environ.get("DATABASE_USER_PASSWORD")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")


def get_db():
    if "db" not in g:
        g.db = init_db_connection().connect()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


# For the following two functions, c.f. 
# https://github.com/GoogleCloudPlatform/serverless-expeditions/blob/main/cloud-run-cloud-sql/main.py


def init_db_connection():
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    }
    return init_unix_connection_engine(db_config)


def init_unix_connection_engine(db_config):
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            host="127.0.0.1",
            port=3306,
            username=DATABASE_USER_NAME,
            password=DATABASE_USER_PASSWORD,
            database=DATABASE,
            query={"unix_socket": "/cloudsql/{}".format(CLOUD_SQL_CONNECTION_NAME)},
        ),
        **db_config,
    )
    pool.dialect.description_encoding = None
    return pool


def get_post(post_id):
    db = get_db()
    query = text(
        """
        SELECT 
            post_id, 
            title, 
            body, 
            created, 
            p.user_id, 
            username,
            image_url
        FROM 
            post p 
        JOIN 
            user u ON p.user_id = u.user_id
        WHERE 
            p.post_id = :post_id
        """
    )
    post = db.execute(query, {"post_id": post_id}).fetchone()
    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    return post


def get_previous_post(post_id):
    db = get_db()
    query = text(
        """
    SELECT 
        post_id, 
        title, 
        body, 
        created, 
        p.user_id, 
        username,
        image_url
    FROM 
        post p 
    JOIN 
        user u ON p.user_id = u.user_id
    WHERE
        created < (
            SELECT
                created
            FROM 
                post
            WHERE 
                post_id = :post_id)
    ORDER BY
        created DESC
    LIMIT 1
    """,
    )
    previous_post = db.execute(query, {"post_id": post_id}).fetchone()
    return previous_post


def get_next_post(post_id):
    db = get_db()
    query = text(
        """
    SELECT 
        post_id, 
        title, 
        body, 
        created, 
        p.user_id, 
        username,
        image_url
    FROM 
        post p 
    JOIN 
        user u ON p.user_id = u.user_id
    WHERE
        created > (
            SELECT
                created
            FROM 
                post
            WHERE 
                post_id = :post_id)
    ORDER BY
        created ASC
    LIMIT 1
    """,
    )
    next_post = db.execute(query, {"post_id": post_id}).fetchone()
    return next_post


def get_image_name(post_id):
    db = get_db()
    query = text(
        """
    SELECT 
        image_name
    FROM 
        post p 
    WHERE
        post_id = :post_id
    """,
    )
    image_name = db.execute(query, {"post_id": post_id}).fetchone()[0]
    return image_name
