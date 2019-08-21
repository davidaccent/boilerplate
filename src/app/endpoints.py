from starlette import status
from starlette.authentication import requires
from starlette.config import Config as config
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse
from starlette_auth.tables import User

from app import db
from app.forms import UserForm
from app.globals import templates


class Home(HTTPEndpoint):
    async def get(self, request):
        template = "home.html"
        context = {"request": request}
        return templates.TemplateResponse(template, context)


class Users(HTTPEndpoint):
    async def get(self, request):
        template = "users.html"
        users = User.query.all()
        context = {"request": request, "users": users}
        return templates.TemplateResponse(template, context)


class UserDetail(HTTPEndpoint):
    async def get(self, request):
        template = "details.html"
        user_id = request.path_params["user_id"]
        user = User.query.get_or_404(user_id)
        context = {"request": request, "user": user}
        return templates.TemplateResponse(template, context)


class UserUpdate(HTTPEndpoint):
    async def get(self, request):
        user_id = request.path_params["user_id"]
        user = User.query.get_or_404(user_id)

        form = UserForm(obj=user)

        template = "update.html"

        context = {"request": request, "user": user, "form": form}
        return templates.TemplateResponse(template, context)

    async def post(self, request):
        user_id = request.path_params["user_id"]
        user = User.query.get_or_404(user_id)

        data = await request.form()
        form = UserForm(data, obj=user)

        if not form.validate():
            template = "update.html"
            context = {"request": request, "user": user, "form": form}
            return templates.TemplateResponse(template, context)

        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_active = form.is_active.data

        user.save()

        return RedirectResponse(url=request.url_for("users"), status_code=302)


class UserDelete(HTTPEndpoint):
    @requires("authenticated", redirect="auth:login")
    async def get(self, request):
        template = "delete.html"
        user_id = request.path_params["user_id"]
        user = User.query.get_or_404(user_id)
        delete = ""

        if User.query.count() < 2:
            delete = "disable"
        elif user_id == request.user.id:
            delete = "active"
        else:
            delete = "enable"

        context = {"request": request, "user": user, "delete": delete}
        return templates.TemplateResponse(template, context)

    @requires("authenticated", redirect="auth:login")
    async def post(self, request):
        user_id = request.path_params["user_id"]
        user = User.query.get_or_404(user_id)

        if User.query.count() > 1:
            user.delete()

        if user.id == request.user.id:
            request.session.clear()

        return RedirectResponse(url=request.url_for("users"), status_code=302)
