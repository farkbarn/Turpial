# -*- coding: utf-8 -*-

# Widget for HTML view in Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
import gtk
import webkit
import gobject

class HtmlView(gtk.VBox, gobject.GObject):
    __gsignals__ = {
        "action-request": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
        "link-request": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
        "load-started": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
        "load-finished": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, coding='utf-8'):
        gobject.GObject.__init__(self)
        gtk.VBox.__init__(self, False)
        
        self.coding = coding
        self.uri = 'file://' + os.path.dirname(__file__)
        self.settings = webkit.WebSettings()
        self.settings.set_property('enable-default-context-menu', False)
        '''
        self.settings.enable_java_applet = False
        self.settings.enable_plugins = False
        self.settings.enable_page_cache = True
        self.settings.enable_offline_web_application_cache = False
        self.settings.enable_html5_local_storage = False
        self.settings.enable_html5_database = False
        self.settings.enable_default_context_menu = False
        '''
        self.view = webkit.WebView()
        self.view.set_settings(self.settings)
        self.view.connect('load-started', self.__started)
        self.view.connect('load-finished', self.__finished)
        self.view.connect('console-message', self.__console_message)
        self.view.connect('navigation-policy-decision-requested', self.__process)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.view)
        
        self.pack_start(scroll, True, True, 0)
    
    def __console_message(self, view, message, line, source_id, data=None):
        print "%s <%s:%i>" % (message, source_id, line)
        return True
    
    def __process(self, view, frame, request, action, policy, data=None):
        url = request.get_uri()
        if url is None:
            pass
        elif url.startswith('cmd:'):
            policy.ignore()
            self.emit('action-request', url[4:])
        elif url.startswith('link:'):
            policy.ignore()
            self.emit('link-request', url[5:])
        policy.use()
    
    def __started(self, widget, frame):
        self.emit('load-started')
    
    def __finished(self, widget, frame):
        self.emit('load-finished')
    
    def load(self, url):
        gobject.idle_add(self.view.load_uri, url)
        
    def render(self, html):
        gobject.idle_add(self.view.load_string, html, "text/html", self.coding, 
            self.uri)
    
    def update_element(self, id_, html, extra=''):
        html = html.replace('"', '\\"')
        script = "$('%s').html(\"%s\"); %s" % (id_, html, extra)
        self.execute(script)
        
    def append_element(self, id_, html, extra=''):
        html = html.replace('"', '\\"')
        script = "$('%s').append(\"%s\"); %s" % (id_, html, extra)
        self.execute(script)
        
    def execute(self, script):
        #print script
        script = script.replace('\n', ' ')
        self.view.execute_script(script)
    
    def stop(self):
        self.view.stop_loading()

gobject.type_register(HtmlView)
