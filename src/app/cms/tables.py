import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_utils import Ltree, LtreeType
from starlette_core.database import Base, Session

from app.db import db

from .exceptions import PageMoveError


class PageManager:
    @classmethod
    def root(cls) -> orm.Query:
        """ Get all root pages """

        qs = Page.query.filter(sa.func.nlevel(Page.path) == 1)
        return qs.order_by(Page.order)

    @classmethod
    def ancestors_of(cls, page: "Page", include_self: bool = False) -> orm.Query:
        """ Get all anscestors of a page """

        qs = Page.query.filter(Page.path.ancestor_of(page.path))
        if not include_self:
            qs = qs.filter(Page.id != page.id)
        # path is prob the most sensible order
        return qs.order_by(Page.path)

    @classmethod
    def descendants_of(cls, page: "Page", include_self: bool = False) -> orm.Query:
        """ Get all descendants of a page """

        qs = Page.query.filter(Page.path.descendant_of(page.path))
        if not include_self:
            qs = qs.filter(Page.id != page.id)
        # path is prob the most sensible order
        return qs.order_by(Page.path)

    @classmethod
    def children_of(cls, page: "Page") -> orm.Query:
        """ Get all children of a page """

        qs = Page.query.filter(
            Page.path.descendant_of(page.path),
            sa.func.nlevel(Page.path) == len(page.path) + 1,
        )
        return qs.order_by(Page.order)

    @classmethod
    def siblings_of(cls, page: "Page", include_self: bool = False) -> orm.Query:
        """ Get all siblings of a page """

        if not page.parent:
            return Page.query.filter(sa.sql.false())

        qs = Page.query.filter(
            Page.path.descendant_of(page.path[:-1]),
            sa.func.nlevel(Page.path) == len(page.path),
        )
        if not include_self:
            qs = qs.filter(Page.id != page.id)
        return qs.order_by(Page.order)

    @classmethod
    def get_next_available_order(cls, parent: "Page" = None) -> int:
        """ Returns the next available order for a page's children """

        if parent:
            sub = cls.children_of(parent).subquery("sub")
        else:
            sub = cls.root().subquery("sub")

        max_order = Session().query(sa.func.max(sub.c.order)).scalar()
        return max_order + 16384 if max_order else 16384


id_seq = sa.Sequence("page_id_seq")


class Page(Base):
    """
    from app.db import db
    from app.cms.tables import Page

    n = 5

    for x in range(n):
        root = Page(f"Page {x}")
        root.save()
        for y in range(n):
            next = Page(f"Page {x}.{y}", root)
            next.save()
            for z in range(n):
                sub = Page(f"Page {x}.{y}.{z}", next)
                sub.save()
    """

    id = sa.Column(sa.Integer, id_seq, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    path = sa.Column(LtreeType, nullable=False)
    order = sa.Column(sa.types.Float, nullable=False, default=16384)

    parent = orm.relationship(
        "Page",
        primaryjoin=(orm.remote(path) == orm.foreign(sa.func.subpath(path, 0, -1))),
        backref=orm.backref("children", order_by="Page.order"),
        viewonly=True,
    )

    __table_args__ = (sa.Index("ix_page_path", path, postgresql_using="gist"),)

    def __init__(self, title: str, parent: "Page" = None, order: float = None) -> None:
        _id = db.engine.execute(id_seq)
        _ltree_id = Ltree(str(_id))
        self.id = _id
        self.title = title
        self.path = _ltree_id if parent is None else parent.path + _ltree_id
        self.order = order or PageManager.get_next_available_order(parent)

    def __str__(self):
        return self.title

    @property
    def depth(self) -> int:
        return len(self.path) - 1

    def ancestors(self, include_self: bool = False) -> orm.Query:
        return PageManager.ancestors_of(self, include_self)

    def descendants(self, include_self: bool = False) -> orm.Query:
        return PageManager.descendants_of(self, include_self)

    def is_ancestor_of(self, page: "Page") -> bool:
        if len(self.path) >= len(page.path):
            return False
        return page.path[: len(self.path)] == self.path

    def is_descendant_of(self, page: "Page") -> bool:
        if len(self.path) <= len(page.path):
            return False
        return self.path[: len(page.path)] == page.path

    def move_to(self, new_parent: "Page") -> None:
        if new_parent.id == self.id:
            raise PageMoveError("cannot move a page to itself")
        if new_parent.is_descendant_of(self):
            raise PageMoveError("cannot move a page to one of its descendants")

        new_path = new_parent.path + self.path[1:]
        for page in self.descendants().all():
            page.path = new_path + page.path[len(self.path) :]
        self.path = new_path

    def siblings(self, include_self: bool = False) -> orm.Query:
        return PageManager.siblings_of(self, include_self)
