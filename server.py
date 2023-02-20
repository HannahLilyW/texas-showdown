import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
    loader=PackageLoader("server"),
    autoescape=select_autoescape()
)


class Root(object):
    @cherrypy.expose
    def index(self):
        template = env.get_template("index.html")
        return template.render()


if __name__ == '__main__':
    cherrypy.quickstart(Root(), config={
        '/styles.css': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': "/mnt/c/Users/hanna/texas-showdown/static/styles.css"
        },
        '/jQuery.js': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': "/mnt/c/Users/hanna/texas-showdown/static/jquery-3.6.1.min.js"
        },
        'index.js': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': "/mnt/c/Users/hanna/texas-showdown/static/index.js"
        }
    })
