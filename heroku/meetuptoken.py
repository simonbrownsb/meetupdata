# -*- coding: utf-8 -*-

#
# Heroku app for OAuth2 implicit-flow access_token fetch.
#
# It just serves up some static javascript that manages the OAuth2 flow,
# with hardwired ids and URLs.
#
# Deployed to meetuptoken.herokuapp.com.
#

import sys
import os

import cherrypy
import jinja2


class MeetupTokenApp(object):
    def __init__(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('static'))

    @cherrypy.expose
    def index(self):
        """
        Serve the HTML for the application.
        """
        cherrypy.config['tools.encode.on'] = True
        cherrypy.config['tools.encode.encoding'] = 'utf-8'
        cherrypy.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        tmpl = self.env.get_template('meetuptoken.html')
        return tmpl.render()

    @cherrypy.expose
    def redirect(self, *args, **kwargs):
        """
        Redirect back to the main application page
        """
        return self.index()


def main(argv):
    """
    Start up the meetup-token web application.
    """
    config = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 9001)),

        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
            'tools.staticdir.dir': 'static',
        }
    }
    if '-v' not in argv:
        cherrypy.config.update({'environment': 'embedded'})
    cherrypy.quickstart(MeetupTokenApp(), '/', config=config)


if __name__ == '__main__':
    main(sys.argv)

