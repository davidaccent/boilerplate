from wtforms import fields, form, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms_alchemy import ModelForm

from app.blog.tables import Blog


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        only = ["title", "meta_description", "author", "post_body"]
