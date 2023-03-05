from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from src.blueprints.auth import login_required
from src.utils.db import (
    get_db,
    get_post,
    get_previous_post,
    get_next_post,
    get_image_name,
)
from src.utils.storage import create_blob, upload_img_to_blob, delete_blob
from sqlalchemy import text

from uuid import uuid4

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
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
        created = (
        SELECT 
            MAX(created)
        from post
        )
    """
    )
    post = db.execute(query).fetchone()
    if post is None:
        previous_post = None
        next_post = None
    else:
        previous_post = get_previous_post(post.post_id)
        next_post = get_next_post(post.post_id)
    return render_template(
        "blog/index.html", post=post, previous_post=previous_post, next_post=next_post
    )


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            image_name = None
            image_url = None
            if "img" in request.files:
                img = request.files["img"]
                if img.filename != "":
                    image_name = uuid4().hex + "_" + img.filename
                    blob = create_blob(image_name)
                    image_url = upload_img_to_blob(img, blob)
            db = get_db()
            query = text(
                """
            INSERT INTO post 
                (title, body, user_id, image_name, image_url)
            VALUES 
                (:title, :body, :user_id, :image_name, :image_url)
            """
            )
            db.execute(
                query,
                {
                    "title": title,
                    "body": body,
                    "user_id": g.user.user_id,
                    "image_name": image_name,
                    "image_url": image_url,
                },
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            old_image_name = get_image_name(id)
            if old_image_name is not None:
                delete_blob(old_image_name)
            image_url = None
            image_name = None
            if "img" in request.files:
                img = request.files["img"]
                if img.filename != "":
                    image_name = uuid4().hex + "_" + img.filename
                    blob = create_blob(image_name)
                    image_url = upload_img_to_blob(img, blob)
            db = get_db()
            query = text(
                """
                UPDATE 
                    post 
                SET 
                    title = :title, 
                    body = :body, 
                    image_name = :image_name, 
                    image_url = :image_url
                WHERE 
                    post_id = :post_id
                """
            )
            db.execute(
                query,
                {
                    "title": title,
                    "body": body,
                    "post_id": id,
                    "image_name": image_name,
                    "image_url": image_url,
                },
            )
            db.commit()
            return redirect(url_for("blog.show_post", id=id))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    image_name = get_image_name(id)
    if image_name is not None:
        delete_blob(image_name)

    db = get_db()
    query = text("DELETE FROM post WHERE post_id = :post_id")
    db.execute(query, {"post_id": id})
    db.commit()
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>")
def show_post(id):
    post = get_post(id)
    previous_post = get_previous_post(id)
    next_post = get_next_post(id)
    return render_template(
        "blog/index.html", post=post, previous_post=previous_post, next_post=next_post
    )


@bp.route("/history")
def history():
    db = get_db()
    query = text(
        """
    SELECT
        post_id,
        title, 
        created
    FROM 
        post
    ORDER BY 
        created DESC
    """
    )
    posts = db.execute(query).fetchall()
    return render_template("blog/history.html", posts=posts)


