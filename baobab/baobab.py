import os
import importlib.util
import re


class Page(object):
    """
    The Page object is used to generate an html page for each branch.py file
    """
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.page_directory = os.path.dirname(os.path.realpath(self.settings_path))
        spec = importlib.util.spec_from_file_location("local_settings", self.settings_path)
        local_settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_settings)
        self.settings = Application.main.base_settings.copy()
        self.settings.update(local_settings.settings)
        self.content = None

    def get_layout(self):
        with open(self.get_layout_path(), 'rb') as layout:
            return layout.read().decode('utf8')

    def get_layout_path(self):
        if self.has_local_layout():
            return self.get_local_layout_path()
        else:
            return Application.main.get_layout_path()

    def has_local_layout(self):
        return os.path.isfile(self.get_local_layout_path())

    def get_local_layout_path(self):
        return os.path.join(self.page_directory, self.settings['layout_files'])

    def get_local_partials_directory(self):
        return os.path.join(self.page_directory, self.settings['partials'])

    def get_partial_path(self, name):
        local = Application.build_partial_filename(self.get_local_partials_directory(), name)
        application = Application.main.get_partial_path(name)
        if os.path.isfile(local):
            return local
        elif os.path.isfile(application):
            return application

    def get_partial(self, name):
        path = self.get_partial_path(name)
        if path:
            with open(self.get_partial_path(name), 'rb') as layout:
                return layout.read().decode('utf8')

    def render(self, content):
        open_delimiter = re.escape(self.settings["open_delimiter"])
        close_delimiter = re.escape(self.settings["close_delimiter"])
        pattern = re.compile(open_delimiter+"([a-zA-Z0-9_]+)"+close_delimiter)
        layout_vars = re.findall(pattern, content)
        print("Layout variables found: \n\t{vars}".format(vars=layout_vars))
        for var in layout_vars:
            search = "{open_del}{var}{close_del}".format(
                open_del=self.settings["open_delimiter"],
                var=var,
                close_del=self.settings["close_delimiter"],
            )
            var_value = self.settings.get(var)
            if var_value:
                print("Rendering: \n\tvar: {var} \n\tval: {val}".format(var=var, val=var_value))
                rendered_variable = self.render(var_value)
                content = content.replace(search, rendered_variable)
            else:
                partial = self.get_partial(var)
                if not partial:
                    continue
                partial_path = self.get_partial_path(var)
                if partial_path:
                    partial_path = partial_path.replace(Application.main.root, "")
                print("Rendering partial \n\t'{partial}'".format(partial=partial_path))
                rendered_partial = self.render(partial)
                content = content.replace(search, rendered_partial)
        self.content = content
        # render hook here
        return content

    def build(self):
        print("Building \n\t'[root]{path}'".format(path=self.page_directory.replace(Application.main.root, "")))
        content = self.render(self.get_layout())
        write_path = os.path.join(self.page_directory, self.settings["destination_file"])
        with open(write_path, "wb+") as f:
            f.write(content.encode('utf8'))


class Application(object):
    """
    The Application object is the entrypoint to generate the site.
    """
    main = None

    def __init__(self, root):
        Application.main = self
        self.root = root
        self.base_settings = __import__("branch").settings

    def get_layout(self):
        with open(self.get_layout_path(), 'r') as root_layout:
            return root_layout.read()

    def get_layout_path(self):
        return os.path.join(self.root, self.base_settings['layout_files'])

    def get_partials_directory(self):
        return os.path.join(self.root, self.base_settings['partials'])

    def get_partial_path(self, name):
        return Application.build_partial_filename(self.get_partials_directory(), name)

    @staticmethod
    def build_partial_filename(partial_dir, name):
        return "{dir}/_{name}.html".format(dir=partial_dir, name=name)

    def build(self):
        for root, subdirs, files in os.walk(self.root):
            if "branch.py" in files:
                Page(os.path.join(root, "branch.py")).build()
