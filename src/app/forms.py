from wtforms_alchemy import ModelForm as BaseModelForm
from wtforms import fields, form, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import model_form


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        from starlette_core.database import Session

        return Session()

class UserForm(form.Form):
    first_name = fields.StringField(validators=[validators.InputRequired()])
    last_name = fields.StringField(validators=[validators.InputRequired()])
    email = fields.StringField(validators=[validators.InputRequired()])
    is_active = fields.BooleanField(validators=[validators.optional()])
