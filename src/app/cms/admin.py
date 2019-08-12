from starlette_admin.admin import ModelAdmin
from wtforms import form
from wtforms_alchemy import ModelForm

from .tables import Page, PageManager


class PageForm(ModelForm):
    class Meta:
        model = Page
        only = ["title"]


class PageAdmin(ModelAdmin):
    section_name = "CMS"
    collection_name = "Pages"
    model_class = Page
    list_field_names = ["title"]
    paginate_by = 10
    order_enabled = False
    search_enabled = False
    create_form = PageForm
    update_form = PageForm
    delete_form = form.Form
    list_template = "cms/admin/page/list.html"

    @classmethod
    def get_parent(cls, request):
        parent_id = request.query_params.get("parent")
        if parent_id:
            return Page.query.get_or_404(parent_id)
        return None

    @classmethod
    def get_context(cls, request):
        context = super().get_context(request)
        context.update({"parent": cls.get_parent(request)})
        return context

    @classmethod
    def get_list_objects(cls, request):
        parent = cls.get_parent(request)
        if parent:
            return parent.children
        else:
            return PageManager.root().all()

    @classmethod
    async def do_create(cls, form, request):
        parent = cls.get_parent(request)
        instance = cls.model_class(title=form.title.data, parent=parent)
        instance.save()
        return instance
