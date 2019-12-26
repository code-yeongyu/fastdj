import os
from template import Template


class Field:
    def __init__(self, field_name, field_type=None, **kwargs):
        self.field_name = field_name
        self.field_type = field_type
        self.app_name = kwargs.get('app_name')
        self.serializers = kwargs.get('serializers', {})
        self.options = kwargs.get('options', [])
        self.choices = kwargs.get('choices')
        self.not_to_serialize = kwargs.get('not_to_serialize', False)
        template = kwargs.get('template')

        if template == Template.model_owner:
            self.field_type = "ForeignKey"
            self.options = [
                "'auth.user'", f"related_name='{self.app_name}_{field_name}'",
                "on_delete=models.CASCADE", "null=False"
            ]
            self.serializers = {
                "field": "ReadOnlyField",
                "options": ["source='writer.username'"]
            }

    def get_code(self):
        if not self.choices == None:
            self.options.append(f"choices={self.choices}")
        options_str = ""
        for option in self.options:
            options_str += option + ", "
        options_str = options_str[:-2]  # to remove last ", "
        code = ""
        code += f"\t{self.field_name} = models.{self.field_type}({options_str})\n"
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
            code += f"\t{field.field_name} = serializers.{field_object}({options_str})\n"
        code += "\tclass Meta:\n"
        code += f"\t\tmodel = {self.name}\n"
        fields_str = ""
        for field in self.fields:
            if field.not_to_serialize:
                continue
            fields_str += field.field_name + ", "
        fields_str = fields_str[:-2]  # to remove last ", "
        code += f"\t\tfields = ({fields_str})"
        return code

    def get_model_code(self):
        code = f"class {self.name}(models.Model):\n"
        for field in self.fields:
            code += field.get_code()
        return code


class ViewSet:
    def __init__(self, app_name, name, **kwargs):
        self.name = name
        self.app_name = app_name
        self.template = kwargs.get('template')
        self.model_name = kwargs.get('model_name')
        self.options = kwargs.get('options', list())
        self.permissions = kwargs.get('permissions', "")
        self.url_getters = kwargs.get('url_getters', "")
        self.SERIALIZER = f"{self.model_name}Serializer"
        self.modules = list()
        self.modules.append(
            f"from {self.app_name}.model import {self.model_name}")
        self.modules.append(
            f"from {self.app_name}.serializers import {self.SERIALIZER}")
        self.owner_field_name = kwargs.get('owner_field_name')
        self.code = str()

    def _use_generic_based_template(self):
        self.modules.append("from rest_framework import generics")
        self.modules.append("from rest_framework import permissions")

    def _get_template_code(self):
        code = f"\tqueryset = {self.model_name}.objects.all()\n"
        code += f"\tserializer_class = {self.SERIALIZER}\n"
        code += f"\tpermission_classes = (permissions.{self.permissions})\n"
        return code

    def update_code(self):  # test required
        self.code = ""
        self.modules.append("from rest_framework.response import Response")
        if self.template == Template.detail_view:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetreiveAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.detail_view_u:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetreiveUpdateAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.detail_view_d:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetreiveDestroyAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.detail_view_ud:
            self._use_generic_based_template()
            self.code = f"class {self.name}(generics.RetreiveUpdateDestroyAPIView):\n"
            self.code += self._get_template_code()
        elif self.template == Template.all_objects_view:
            self._use_generic_based_template()
            self.modules.append("from django.http import JsonResponse")
            self.code = f"class {self.name}(generics.ListAPIView, APIView):\n"
            self.code += self._get_template_code()
            self.code += "\n\tdef post(self, request):\n"
            self.code += "\t\tif request.user.is_authenticated:\n"
            self.code += f"\t\t\tserializer = {self.SERIALIZER}(data=request.data)\n"
            self.code += f"\t\t\tif serializer.is_valid():\n"
            self.code += f"\t\t\t\tserializer.save({self.owner_field_name}=request.user)\n"
            self.code += f"\t\t\t\treturn JsonResponse(serializer.data, status=status.HTTP_201_CREATED)\n"
            self.code += f"\t\t\treturn Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)\n"
            self.code += f"\t\treturn Response(status=status.HTTP_401_UNAUTHORIZED)\n"
        elif self.template == Template.filter_objects_view:
            self.modules.append(
                "from rest_framework.decorators import api_view")
            self.modules.append(
                "from django.shortcuts import get_object_or_404")
            self.code = f"@api_view(['GET'])\n"
            self.code += f"def {self.name}(request, {self.url_getters})\n"
            options_str = ""
            for option in self.options:
                options_str += option + ", "
            options_str = options_str[:-2]  # to remove last ", "
            self.code += f"\tobject_to_return = get_object_or_404({self.model_name}, {options_str}).values()\n"
            self.code += f"\treturn Response(object_to_return)"
        elif self.template == Template.user_register_view:
            self.modules.append(
                "from rest_framework.decorators import api_view")
            self.modules.append(
                f"from {self.app_name}.forms import RegisterForm")
            self.code = """@api_view(['POST'])
def register(request):  # 회원가입
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.save()
        profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
            """
        else:
            self.code = ""

    def get_code(self):
        return self.code


class App:
    def __init__(self, name, project_name):
        self.name = name
        self.project_name = project_name
        self.models = list()
        self.views = list()
        self.models_code = ""
        self.views_code = ""
        self.APP_PATH = f"{os.getcwd()}/{self.project_name}/{self.name}/"

    def add_model(self, model):
        self.models.append(model)

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
        code += f"from {self.name}.models import {self.name}\n"

        for model in self.models:
            code += f"class {model.name}Serializer(serializers.ModelSerializer):\n"
            code += model.get_serializers_code()
            code += "\n"
        return code

    def get_forms_code(self):
        # form feature currently only supported on custom profile features
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

    def get_views_code(self):
        modules_code = ""
        code = ""
        modules = list()
        for view in self.views:
            view.update_code()
            for module in set(view.modules):
                modules.append(module)
            code += view.get_code() + "\n"
        for module in set(modules):  # used set to remove duplicates
            modules_code += module + "\n"
        return modules_code + "\n" + code

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