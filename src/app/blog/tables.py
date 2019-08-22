import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from starlette_core.database import Base


class Blog(Base):
    id = sa.Column(
        sa.Integer, nullable=False, primary_key=True, index=True, unique=True
    )
    title = sa.Column(sa.String(120), nullable=False, unique=True)
    meta_description = sa.Column(sa.String(120))
    author = sa.Column(
        sa.String(120), nullable=False
    )  # possibly take from active user_id
    post_body = sa.Column(sa.Text())
    date_created = sa.Column(sa.DateTime)
    last_updated = sa.Column(sa.DateTime)
    last_updated_by = sa.Column(sa.String(120))  # possibly take from active user_id
    is_live = sa.Column(sa.Boolean, nullable=False, default=False)
    # images to be stores in media?
