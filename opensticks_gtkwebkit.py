'''
Derived from pybrowser.py ( https://gist.github.com/kklimonda/890640 (License unknown)) 
Derivation by Brad Porter 2018

While the license is unknown, this file is not likely to be used except in open source, free versions.  For platforms other than linux, this would be replaced, by another GUI.
'''
                 
import sys
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gdk, WebKit
import readsticks as rs

class BrowserTab(Gtk.VBox):
    db_id=0
    db_id_next=0
    db_id_prev=0
    volume=''
    mainbook=''
    pgformat='scroll' # set default: scroll or 2col
    def __init__(self, *args, **kwargs):
        super(BrowserTab, self).__init__(*args, **kwargs)

        go_button = Gtk.Button("go to ...")
        go_button.connect("clicked", self._load_url)
        pgformat_button = Gtk.Button("Toggle Page Format")
        pgformat_button.connect("clicked", self._pgformat_toggle)
        self.pgformatLabel = Gtk.Label()
        self.pgformatLabel.set_text("Scroll")
        #self.pgformatLabel.set_justify(Gtk.Justification.LEFT)
        #So replace label.set_justify(gtk.JUSTIFY_LEFT) with 
        self.pgformatLabel.set_alignment(0, 0) #and it should work.
        self.url_bar = Gtk.Entry()
        self.url_bar.connect("activate", self._load_url)
        self.webview = WebKit.WebView()
        self.show()

        self.go_back = Gtk.Button("Back")
        self.go_back.connect("clicked", lambda x: self.webview.go_back())
        self.go_forward = Gtk.Button("Forward")
        self.go_forward.connect("clicked", lambda x: self.webview.go_forward())

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.webview)

        find_box = Gtk.HBox()
        close_button = Gtk.Button("Close")
        close_button.connect("clicked", lambda x: find_box.hide())
        self.find_entry = Gtk.Entry()
        self.find_entry.connect("activate",
                                lambda x: self.webview.search_text(self.find_entry.get_text(),
                                                                   False, True, True))
        prev_button = Gtk.Button("Previous")
        next_button = Gtk.Button("Next")
        prev_button.connect("clicked",
                            lambda x: self.webview.search_text(self.find_entry.get_text(),
                                                               False, False, True))
        next_button.connect("clicked",
                            lambda x: self.webview.search_text(self.find_entry.get_text(),
                                                               False, True, True))
        self.goto_entry = Gtk.Entry()
        self.goto_entry.connect("activate",
                                lambda x: self.webview.load_html_string(self.getChapterString('','',-1,self.goto_entry.get_text()),
                            base_uri='file:///media/brad/002C-270E/rsync/gospeldata/data/_scriptures_pgp_000/')) 
        #prevpg_button = Gtk.Button("Previous")
        #nextpg_button = Gtk.Button("Next")
        #prevpg_button.connect("clicked",
        #                    lambda x: self.webview.search_text(self.find_entry.get_text(),
        #                                                       False, False, True))
        #nextpg_button.connect("clicked",
        #                    lambda x: self.webview.search_text(self.find_entry.get_text(),
        #                                                       False, True, True))
        find_box.pack_start(close_button, False, False, 0)
        find_box.pack_start(self.goto_entry, False, False, 0)
        #find_box.pack_start(prevpg_button, False, False, 0)
        #find_box.pack_start(nextpg_button, False, False, 0)
        find_box.pack_start(self.find_entry, False, False, 0)
        find_box.pack_start(prev_button, False, False, 0)
        find_box.pack_start(next_button, False, False, 0)
        self.find_box = find_box

        url_box = Gtk.HBox()
        url_box.pack_start(self.go_back, False, False, 0)
        url_box.pack_start(self.go_forward, False, False, 0)
        url_box.pack_start(self.url_bar, True, True, 0)
        url_box.pack_start(go_button, False, False, 0)

        sticks_box = Gtk.HBox()
        sticks_box.pack_start(pgformat_button, False, False, 0)
        sticks_box.pack_start(self.pgformatLabel, True, True, 0)

        self.pack_start(url_box, False, False, 0)
        self.pack_start(sticks_box, False, False, 0)
        self.pack_start(scrolled_window, True, True, 0)
        self.pack_start(find_box, False, False, 0)

        url_box.show_all()
        sticks_box.show_all()
        scrolled_window.show_all()

    def _load_url(self, widget):
        url = self.url_bar.get_text()
        if not "://" in url:
            url = "http://" + url
        self.webview.load_uri(url)

    def getChapterString(self, volume, mainbook, db_id, gotoString):
        if(self.pgformat=='2col'):
           self.volume, self.mainbook, self.db_id_prev, self.db_id_next, htmlstring=rs.getChapter_2col(volume, mainbook, db_id, gotoString)
        elif(self.pgformat=='scroll'):
           self.volume, self.mainbook, self.db_id_prev, self.db_id_next, htmlstring=rs.getChapter_scroll(volume, mainbook, db_id, gotoString)
        #next line is in rs
        #addcss='<head> <link href=\"sticks.css\" rel=\"stylesheet\" type=\"text/css\" /></head>'
        #
        return htmlstring
     
    def nextpage(self):
        self.webview.load_html_string(self.getChapterString(self.volume, self.mainbook, self.db_id_next,''), base_uri='file:///media/brad/002C-270E/rsync/gospeldata/data/_scriptures_pgp_000/')
    
    def prevpage(self):
        self.webview.load_html_string(self.getChapterString(self.volume, self.mainbook, self.db_id_prev,''), base_uri='file:///media/brad/002C-270E/rsync/gospeldata/data/_scriptures_pgp_000/')

    def _pgformat_toggle(self, widget):
        if(self.pgformat=='2col'):
            self.pgformat='scroll'
            self.pgformatLabel.set_text("Scroll")
            print 'scroll'
        else:
            self.pgformat='2col'
            self.pgformatLabel.set_text("Two Column")
            print '2col'

class Browser(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)

	# create notebook and tabs
	self.notebook = Gtk.Notebook()
	self.notebook.set_scrollable(True)

	# basic stuff
        self.tabs = []
	self.set_size_request(1200,600)

        # create a first, empty browser tab
        self.tabs.append((self._create_tab(), Gtk.Label("New Tab")))
        self.notebook.append_page(*self.tabs[0])
        self.add(self.notebook)

	# connect signals
        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self._key_pressed)
        self.notebook.connect("switch-page", self._tab_changed)

        self.notebook.show()
        self.show()

    def _tab_changed(self, notebook, current_page, index):
        if not index:
            return
        title = self.tabs[index][0].webview.get_title()
        if title:
            self.set_title(title)

    def _title_changed(self, webview, frame, title):
        current_page = self.notebook.get_current_page()

        counter = 0
        for tab, label in self.tabs:
            if tab.webview is webview:
                label.set_text(title)
                if counter == current_page:
                    self._tab_changed(None, None, counter)
                break
            counter += 1

    def _create_tab(self):
        tab = BrowserTab()
        tab.webview.connect("title-changed", self._title_changed)
        tab.db_id=0
        tab.db_id_next=0
        tab.db_id_prev=0
        return tab

    def _reload_tab(self):
        self.tabs[self.notebook.get_current_page()][0].webview.reload()

    def _close_current_tab(self):
        if self.notebook.get_n_pages() == 1:
            return
        page = self.notebook.get_current_page()
        current_tab = self.tabs.pop(page)
        self.notebook.remove(current_tab[0])

    def _open_new_tab(self):
        current_page = self.notebook.get_current_page()
        page_tuple = (self._create_tab(), Gtk.Label("New Tab"))
        self.tabs.insert(current_page+1, page_tuple)
        self.notebook.insert_page(page_tuple[0], page_tuple[1], current_page+1)
        self.notebook.set_current_page(current_page+1)       

    def _focus_url_bar(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].url_bar.grab_focus()

    def _raise_find_dialog(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].find_box.show_all()
        self.tabs[current_page][0].find_entry.grab_focus()

    def _raise_goto_dialog(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].find_box.show_all()
        self.tabs[current_page][0].goto_entry.grab_focus()
        #view.load_html_string(docp.encode('utf-8'), base_uri='file:///media/brad/002C-270E/rsync/gospeldata/data/_scriptures_pgp_000/') 
        #self.webview.load_html_string('test string', base_uri='file:///media/brad/002C-270E/rsync/gospeldata/data/_scriptures_pgp_000/') 
        #Next line alone works, but should be in BrowserTab
        #self.tabs[self.notebook.get_current_page()][0].webview.load_html_string('test string', base_uri='file:///media/brad/002C-270E/rsync/gospeldata/data/_scriptures_pgp_000/') 
        #win.show_all()

    def _nextpage(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].nextpage()

    def _prevpage(self):
        current_page = self.notebook.get_current_page()
        self.tabs[current_page][0].prevpage()

    def _key_pressed(self, widget, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        mapping = {Gdk.KEY_r: self._reload_tab,
                   Gdk.KEY_w: self._close_current_tab,
                   Gdk.KEY_t: self._open_new_tab,
                   Gdk.KEY_l: self._focus_url_bar,
                   Gdk.KEY_f: self._raise_find_dialog,
                   Gdk.KEY_s: self._raise_goto_dialog,
                   Gdk.KEY_n: self._nextpage,
                   Gdk.KEY_p: self._prevpage,
                   Gdk.KEY_q: Gtk.main_quit}

        if event.state & modifiers == Gdk.ModifierType.CONTROL_MASK \
          and event.keyval in mapping:
            mapping[event.keyval]()
        # every key in find box is considered if below is used
        #else:
        #    mapping[event.keyval]()
        

if __name__ == "__main__":
    Gtk.init(sys.argv)

    browser = Browser()

    Gtk.main()
