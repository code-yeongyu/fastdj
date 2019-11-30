import os, sys, platform
try:
    setup_file = __import__(sys.argv[1])
except:
    print("Try with an argument")
    exit()


class ProjectCommand:  # class about project initializing, like commands
    def __init__(self, name, apps=list()):
        self.name = name
        self.apps = apps

    def setup_venv(self):
        command = ""
        if platform.system() == 'Windows':
            command = "python "
        else:
            command = "python3 "
        command += "-m venv myvenv"
        os.system(command)

    def install_requirements(
            self
    ):  # pip install django djangorestframework django-cors-headers
        os.system("pip install --upgrade pip")
        os.system("pip install django djangorestframework django-cors-headers")

    def start_project(self):
        os.system("django-admin startproject " + str(self.name))

    def create_apps(self):
        origin_directory = os.getcwd()
        os.chdir(f"{os.getcwd()}/{self.name}/")
        for app in self.apps:
            os.system(f"python manage.py startapp {app}")
        os.chdir(origin_directory)


class ProjectConfigurations:
    def __init__(self, project_name):
        self.settings_file_path = f"{os.getcwd()}/{project_name}/{project_name}/settings.py"
        self.urls_file_path = f"{os.getcwd()}/{project_name}/{project_name}/urls.py"

    def load_settings(self):
        settings_file = open(self.settings_file_path, 'r')
        self.settings = settings_file.read()
        settings_file.close()

    def set_language_code(self, language):
        self.settings = self.settings.replace("LANGUAGE_CODE = en-us",
                                              f"LANGUAGE_CODE = '{language}'")

    def set_timezone(self, timezone):
        self.settings = self.settings.replace("TIME_ZONE = 'UTC'",
                                              f"TIMEZONE = '{timezone}'")

    def load_urls(self):
        urls_file = open(self.urls_file_path, 'r')
        self.urls = urls_file.read()
        urls_file.close()

    def add_module(self, module_name):
        installed_apps_index = self.settings.find("INSTALLED_APPS")
        last_module_index = self.settings.find(
            "]", installed_apps_index) - 1  # except itself and the '\n
        self.settings = self.settings[:
                                      last_module_index] + "\n\t# added by fastdj\n\t'" + module_name + "'," + self.settings[
                                          last_module_index:]

    def add_installed_modules(self):  # djangorestframework django-cors-headers
        modules = ['rest_framework', 'rest_framework.authtoken', 'corsheaders']
        for module in modules:
            self.add_module(module)

    def add_token_login_model(self):  # token login model
        self.settings += "\n# added by fastdj\nREST_FRAMEWORK = {\n\t'DEFAULT_AUTHENTICATION_CLASSES': (\n\t\t'rest_framework.authentication.BasicAuthentication',\n\t\t'rest_framework.authentication.TokenAuthentication',\n\t),\n}\n"

    def set_cross_origin_all(self):  # cors origin allow all
        self.settings += "\n# added by fastdj\nCORS_ORIGIN_ALLOW_ALL = True\nCORS_ALLOW_CREDENTIALS = True\n"

    def set_allowed_hosts_all(self):  # set allowed hosts to all
        self.settings = self.settings.replace("ALLOWED_HOSTS = []",
                                              "ALLOWED_HOSTS = ['*']")

    def add_url_path(self, app_name):
        urlpatterns_index = self.urls.find("urlpatterns")
        last_path_index = self.urls.find(
            "]", urlpatterns_index) - 1  # except itself and the '\n
        self.urls = f"{self.urls[:last_path_index]}\n\t# added by fastdj\n\tpath('{app_name}/', include('{app_name}.urls', name='{app_name}')){self.urls[last_path_index:]}\n"

    def save_settings(self):
        file = open(self.settings_file_path, 'w')
        file.write(self.settings)
        file.close()

    def save_urls(self):
        file = open(self.urls_file_path, 'w')
        file.write(self.urls)
        file.close()


class Model:
    def __init__(self,
                 name,
                 field,
                 template=None,
                 serializer=None,
                 options=None):
        self.name = name
        self.template = template
        self.serializer = serializer
        self.options = options


class View:
    def __init__(self,
                 name,
                 field,
                 template=None,
                 options=None,
                 permissions=None,
                 url_getters=None):
        self.name = name
        self.field = field
        self.template = template
        self.options = options
        self.permissions = permissions
        self.url_getters = url_getters


class Project:
    project_name = setup_file.project_name
    apps = setup_file.apps
    user_model = setup_file.user_model

    def __init__(self):
        self.cmd = ProjectCommand(self.project_name, self.apps.keys())
        self.confs = ProjectConfigurations(self.project_name)
        try:
            self.timezone = setup_file.timezone
            self.language = setup_file.language
        except:
            pass

    def menu(self):
        print("0. Create a new venv")
        print("1. Create your project")
        option_choice = int(input("Type here: "))
        if (option_choice == 0):
            self.create_venv()
        elif (option_choice == 1):
            self.create_project()

    def create_venv(self):
        self.cmd.setup_venv()
        if platform.system() == "windows":
            print(
                "Type 'call myvenv/scripts/activate', re-execute the script and type 1!"
            )
        else:
            print(
                "Type 'source myvenv/bin/activate', re-execute the script and type 1!"
            )

    def create_project(self):
        self.cmd.install_requirements()
        # setting up project
        self.cmd.start_project()
        self.confs.load_settings()
        self.confs.load_urls()
        self.confs.add_installed_modules()
        self.confs.add_token_login_model()
        self.confs.set_cross_origin_all()
        self.confs.set_allowed_hosts_all()
        if "timezone" in dir(self):
            self.confs.set_timezone(self.timezone)
        if "language" in dir(self):
            self.confs.set_language_code(self.language)
        # creating apps
        self.cmd.create_apps()
        for app in self.apps.keys():
            # create urls.py
            open(f"{os.getcwd()}/{self.project_name}/{app}/urls.py",
                 'w').close()
            self.confs.add_module(app)
            self.confs.add_url_path(app)
        self.confs.save_settings()
        self.confs.save_urls()


def main():
    project = Project()
    project.menu()


main()