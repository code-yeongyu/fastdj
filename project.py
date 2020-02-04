import os, enum
from template import Template


def find_owner_field_in_list(list):
    i = 0
    for item in list:
        if item.template == Template.model_owner:
            return i
        i += 1
    return None


class Field:
    def __init__(self, field_name, field_type=None, **kwargs):
        self.field_name = field_name
        self.field_type = field_type
        self.app_name = kwargs.get('app_name')
        self.serializers = kwargs.get('serializers', {})
        self.options = kwargs.get('options', [])
        self.choices = kwargs.get('choices')
        self.not_to_serialize = kwargs.get('not_to_serialize', False)
        self.template = kwargs.get('template')

        if self.template == Template.model_owner:
            self.field_type = "ForeignKey"
            self.options = [
                "'auth.user'", f"related_name='{self.app_name}_{field_name}'",
                "on_delete=models.CASCADE", "null=False"
            ]
            self.serializers = {
                "field": "ReadOnlyField",
                "options": [f"source='{self.field_name}.username'"]
            }

    def get_code(self):
        if not self.choices == None:
            self.options.append(f"choices={self.choices}")
        options_str = ""
        for option in self.options:
            options_str += option + ", "
        options_str = options_str[:-2]  # to remove last ", "
        code = ""
        code += f"    {self.field_name} = models.{self.field_type}({options_str})\n"
        return code


class Model:
    def __init__(self, name):
        self.name = name
        self.fields = list()

    def add_field(self, field):
        self.fields.append(field)

    def get_serializers_code(self):
        code = ""
        for field in self.fields:
            options_str = ""
            for option in field.serializers.get("options", list()):
                options_str += option + ", "
            options_str = options_str[:-2]  # to remove last ", "
            field_object = field.serializers.get('field')
            if field_object == None:
                break
            code += f"    {field.field_name} = serializers.{field_object}({options_str})\n"
        code += "    class Meta:\n"
        code += f"        model = {self.name}\n"
        fields_str = ""
        for field in self.fields:
            if field.not_to_serialize:
                continue
            fields_str += f"'{field.field_name}', "
        fields_str = fields_str[:-2]  # to remove last ", "
        code += f"        fields = ({fields_str})"
        return code

    def get_model_code(self):
        code = f"class {self.name}(models.Model):\n"
        for field in self.fields:
            code += field.get_code()
        return code


class ViewSet:
    def __init__(self, project_name, app_name, model, template, **kwargs):
        self.app_name = app_name
        self.project_name = project_name
        self.model = model
        self.model_name = model.name
        self.template = template
        self.name = kwargs.get('name')
        self.options = kwargs.get('options', list())
        self.permissions = kwargs.get('permissions', "")
        self.url_getters = kwargs.get('url_getters', "")
        self.SERIALIZER = f"{self.model_name}Serializer"
        self.modules = list()
        self.modules.append(
            f"from {self.app_name}.models import {self.model_name}")
        self.modules.append(
            f"from {self.app_name}.serializers import {self.SERIALIZER}")
        self.modules.append("from rest_framework import status")
        self.code = str()

    def _use_generic_based_template(self):
        self.modules.append("from rest_framework import generics")
        self.modules.append("from rest_framework import permissions")

    def _get_template_code(self):
        code = f"    queryset = {self.model_name}.objects.all()\n"
        code += f"    serializer_class = {self.SERIALIZER}\n"
        code += f"    permission_classes = (permissions.{self.permissions})\n"
        return code

    def get_code(self):
        return self.code

    def update_code(self):
        self.code = ""
        self.modules.append("from rest_framework.response import Response")
        if self.template == Template.detail_view:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetrieveAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.detail_view_u:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetrieveUpdateAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.detail_view_d:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetrieveDestroyAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.detail_view_ud:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetrieveUpdateDestroyAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.all_objects_view:
            owner_field_name = self.model.fields[find_owner_field_in_list(
                self.model.fields)].field_name
            self._use_generic_based_template()
            self.modules.append("from rest_framework.views import APIView")
            self.modules.append("from django.http import JsonResponse")
            self.code = f"""class {self.name}(generics.ListCreateAPIView, APIView):
{self._get_template_code()}
    def perform_create(self, serializer):
        serializer.save({owner_field_name}=request.user)
        """

        elif self.template == Template.filter_objects_view:
            self.modules.append(
                "from rest_framework.decorators import api_view")
            self.modules.append(
                "from django.shortcuts import get_object_or_404")
            self.code = f"@api_view(['GET'])\n"
            self.code += f"def {self.name}(request, {self.url_getters}):\n"
            options_str = ""
            for option in self.options:
                options_str += option + ", "
            options_str = options_str[:-2]  # to remove last ", "
            self.code += f"    object_to_return = get_object_or_404({self.model_name}, {options_str}).values()\n"
            self.code += f"    return Response({self.SERIALIZER}(object_to_return).data)"
        elif self.template == Template.user_register_view:
            self.modules.append(
                "from rest_framework.decorators import api_view")
            self.modules.append(
                f"from {self.app_name}.forms import RegisterForm")
            self.code = f"""@api_view(['POST'])
def register(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.save()
        profile = {self.model_name}.objects.create(user=user)
        serializer = {self.SERIALIZER}(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        {self.model_name}.objects.get(user=user).delete()
        return Response(serializer.errors,
                        status=status.HTTP_406_NOT_ACCEPTABLE)
    return Response(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
            """
        elif self.template == Template.user_profile_view:
            self.modules.append("from rest_framework import permissions")
            self.modules.append("from rest_framework.views import APIView")
            self.code = f"""class ProfileAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            profile = {self.model_name}.objects.get(user=user)
            return Response({self.SERIALIZER}(profile).data,
                            status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        if request.user.is_authenticated:
            profile = {self.model_name}.objects.get(user=user)
            serializer = {self.SERIALIZER}(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
            """
        elif self.template == Template.user_profile_detail_view:
            self.code = f"""class ProfileDetail(APIView):
    def get(self, request, string):
        try:
            user = User.objects.get(username=string)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        profile = {self.model_name}.objects.get_or_create(user=user)
        return Response(
            {self.SERIALIZER}(profile).data,
            status=status.HTTP_200_OK)
            """
        else:
            self.code = ""


class Route:
    code = ""
    is_raw = False

    def __init__(self, view_name, **kwargs):
        self.view_name = view_name
        self.viewset_name_to_route = kwargs.get('viewset_name_to_route',
                                                view_name)
        template = kwargs.get('template')
        if template is not None:
            if not (template == Template.filter_objects_view
                    or template == Template.user_register_view):
                self.viewset_name_to_route += ".as_view()"
            if ("detail" in template) or (
                    template == Template.all_objects_view):
                view_name = ""

        arg_type = kwargs.get('arg_type', Route.template_to_arg_type(template))

        if view_name == "":
            self.code = ""
        else:
            self.code = f"{view_name.lower()}/"
        if arg_type == int:
            self.code += "<int:pk>/"
        elif arg_type == str:
            self.code += "<string>/"

    def get_code(self):
        return self.code

    @staticmethod
    def template_to_arg_type(template):
        if template == Template.detail_view or template == Template.detail_view_u or template == Template.detail_view_d or template == Template.detail_view_ud:
            return int
        if template == Template.user_profile_detail_view:
            return str
        else:
            return None


class App:
    def __init__(self, name, project_name):
        self.name = name
        self.project_name = project_name
        self.models = list()
        self.views = list()
        self.routes = list()
        self.models_code = ""
        self.views_code = ""
        self.APP_PATH = f"{os.getcwd()}/{self.project_name}/{self.name}/"

    def add_model(self, model):
        self.models.append(model)

    def add_route(self, url):
        self.routes.append(url)

    def add_view(self, view):
        self.views.append(view)

    def get_models_code(self):
        code = ""
        if self.name == "custom_user":
            code += "from django.conf import settings\n"
        for model in self.models:
            code += model.get_model_code() + "\n"
        return code

    def get_serializers_code(self):
        code = "from rest_framework import serializers\n"
        for model in self.models:
            code += f"from {self.name}.models import {model.name}\n"
        code += "\n\n"
        for model in self.models:
            code += f"class {model.name}Serializer(serializers.ModelSerializer):\n"
            code += model.get_serializers_code()
            code += "\n\n"
        return code

    def get_forms_code(self):
        # form feature currently supported limitedly for custom profile features
        code = ""
        if self.name == "custom_user":
            code = """from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')"""
        return code

    def get_admin_code(self):
        # admin feature currently supported limitedly for custom profile features
        code = ""
        if self.name == "custom_user":
            code = """from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from custom_user.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin) """
        return code

    def get_views_code(self):
        modules_code = ""
        code = ""
        modules = list()
        for view in self.views:
            view.update_code()
            for module in set(view.modules):
                modules.append(module)
            code += view.get_code() + "\n"
        for module in set(modules):  # set used to remove duplicates
            modules_code += module + "\n"
        return modules_code + "\n\n" + code

    def get_routes_code(self):
        routes_list = list()
        code = f"""from django.urls import path
from {self.name} import views
"""
        routes_code = ""
        for route in self.routes:
            if not route.is_raw:
                routes_list.append(
                    f"    path('{route.get_code()}', views.{route.viewset_name_to_route}, name='{route.view_name}'),\n"
                )
            else:  # for token login view
                routes_list.append(route.get_code())
                code += "from rest_framework.authtoken import views as drf_views"
        routes_list.sort(reverse=True)
        routes_code = ''.join(routes_list)
        code += f"""

urlpatterns = [
{routes_code}
] """
        return code

    def save_models(self):
        file = open(self.APP_PATH + "models.py", 'a')
        file.write(self.get_models_code())
        file.close()

    def save_serializers(self):
        file = open(self.APP_PATH + "serializers.py", 'w')
        file.write(self.get_serializers_code())
        file.close()

    def save_views(self):
        file = open(self.APP_PATH + "views.py", 'w')
        file.write(self.get_views_code())
        file.close()

    def save_forms(self):
        code = self.get_forms_code()
        if code == "":
            return
        file = open(self.APP_PATH + "forms.py", 'w')
        file.write(code)
        file.close()

    def save_admin_file(self):
        code = self.get_admin_code()
        if code == "":
            return
        file = open(self.APP_PATH + "admin.py", 'w')
        file.write(code)
        file.close()

    def save_routings(self):
        file = open(self.APP_PATH + "urls.py", 'w')
        file.write(self.get_routes_code())
        file.close()
