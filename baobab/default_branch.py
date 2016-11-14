import os
from baobab.baobab import Application

app = Application.main

settings = dict()
settings["site_title"] = "éphémère"
settings["site_author"] = "Raphaël Titsworth-Morin"
settings["meta_description"] = "{{site_title}} is creative media by {{site_author}}."
settings["site_tagline"] = "{{meta_description}}"
settings["layout_files"] = "layout.html"
settings["partials"] = "partials"
settings["open_delimiter"] = "{{"
settings["close_delimiter"] = "}}"
settings["destination_file"] = "index.html"
settings["base_layout"] = os.path.join(app.root, settings["layout_files"])
