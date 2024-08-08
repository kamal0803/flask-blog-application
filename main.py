from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
app.config['SECRET_KEY'] = 'my-secret-key'
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class NewBlogForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[DataRequired(), URL(message="Please enter a valid URL!")])
    blog_content = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField(label='Submit Post')


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():

    result = db.session.execute(db.select(BlogPost).order_by(BlogPost.title))
    posts = result.scalars().all()

    return render_template("index.html", all_posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):

    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()

    return render_template("post.html", post=requested_post)

@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():

    from datetime import date

    form = NewBlogForm()

    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        today_date = date.today().strftime("%B %d, %Y")
        author = form.name.data
        body = form.blog_content.data
        img_url = form.img_url.data

        new_post = BlogPost(title=title, subtitle=subtitle, date=today_date, body=body, author=author, img_url=img_url)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):

    post_to_update = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()

    form = NewBlogForm(title=post_to_update.title, subtitle=post_to_update.subtitle,
                             date=post_to_update.date, img_url=post_to_update.img_url,
                             name=post_to_update.author, blog_content=post_to_update.body)

    if form.validate_on_submit():
        post_to_update.title = form.title.data
        post_to_update.subtitle = form.subtitle.data
        post_to_update.author = form.name.data
        post_to_update.body = form.blog_content.data
        post_to_update.img_url = form.img_url.data

        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form, is_edit=True)

@app.route("/delete/<int:post_id>")
def delete_post(post_id):

    post_to_delete = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
