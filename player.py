import gobject
import sys
import gtk

from backend import AudioService
from display import Display

STATE_NULL = 1
STATE_PAUSED = 3
STATE_PLAYING = 4

class AudioInterface(gobject.GObject):

    __gtype_name__ = 'AudioInterface'
    __gsignals__ = {
        'tracks-request': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'play-request': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'pause-request': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }


    def __init__(self):

        gobject.GObject.__init__(self)

        self.state = STATE_NULL

        self.interface = gtk.Builder()
        self.interface.add_from_file('data/interface.ui')

        self.tracks_cache = {}

        self.icons = {
            'artist': gtk.gdk.pixbuf_new_from_file_at_size('data/icons/artist.svg', 16, 16),
            'album': gtk.gdk.pixbuf_new_from_file_at_size('data/icons/album.svg', 16, 16)
            }

        self.window = self.interface.get_object('window')
        self.tracks_liststore = self.interface.get_object('tracks_liststore')
        self.albums_treestore = self.interface.get_object('albums_treestore')
        self.toolbar_layout = self.interface.get_object('toolbar_layout')
        self.albums_treeview = self.interface.get_object('albums_treeview')
        self.tracks_treeview = self.interface.get_object('tracks_treeview')
        self.toolbutton_play = self.interface.get_object('toolbutton_play')

        self.toolbutton_play.connect('clicked', self.play_clicked_cb)
        self.albums_treeview.connect('cursor-changed', self.albums_cursor_changed_cb)
        self.tracks_treeview.connect('row-activated', self.tracks_row_activated_cb)
        self.tracks_liststore.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.albums_treestore.set_sort_column_id(1, gtk.SORT_ASCENDING)

        self.display = Display()
        self.toolbar_layout.pack_start(self.display, True, True, 0)
        self.toolbar_layout.reorder_child(self.display, 1)

        self.window.connect('destroy', lambda *args: sys.exit(0))

        self.window.show_all()


    def play_clicked_cb(self, source):

        if self.state == STATE_PLAYING:
            self.emit('pause-request')
        elif self.state == STATE_PAUSED:
            self.emit('play-request', None)


    def set_state(self, state):

        if self.state == state:
            return

        self.state = state

        if self.state == STATE_NULL:
            self.toolbutton_play.set_stock_id('gtk-media-play')
        elif self.state == STATE_PAUSED:
            self.toolbutton_play.set_stock_id('gtk-media-play')
        elif self.state == STATE_PLAYING:
            self.toolbutton_play.set_stock_id('gtk-media-pause')


    def add_artist(self, artist):
        return self.albums_treestore.append(None, (self.icons['artist'], artist))


    def add_album(self, album, artist_iter):
        return self.albums_treestore.append(artist_iter, (self.icons['album'], album,))


    def add_track(self, track, album_iter):

        if not self.tracks_cache.has_key(album_iter):
            self.tracks_cache[album_iter] = []

        self.tracks_cache[album_iter].append(track)


    def set_tracks(self, tracks):

        self.tracks_liststore.clear()

        for artist, albums in tracks.iteritems():
            for album, tracks in albums.iteritems():
                for title, track in tracks.iteritems():
                    try:
                        track_number = '{0:0>2}'.format(str(int(track['tracknumber'])))
                    except:
                        track_number = ''
                    self.tracks_liststore.append((track['id'], title, track['album'], track['artist'], track_number))


    def albums_cursor_changed_cb(self, source):

        selection = self.albums_treeview.get_selection()
        store, iter = selection.get_selected()

        if store.iter_parent(iter):
            self.emit('tracks-request', {
                'artist': store.get_value(store.iter_parent(iter), 1),
                'album': store.get_value(iter, 1),
                })
        else:
            self.emit('tracks-request', {
                'artist': store.get_value(iter, 1)
                })


    def tracks_row_activated_cb(self, source, selection, column):

        selection = self.tracks_treeview.get_selection()
        store, iter = selection.get_selected()

        id = store.get_value(iter, 0)
        self.emit('play-request', id)


class AudioPlayer(object):

    def __init__(self):

        self.interface = AudioInterface()
        self.interface.connect('tracks-request', self.interface_tracks_request_cb)
        self.interface.connect('play-request', self.interface_play_request_cb)
        self.interface.connect('pause-request', self.interface_pause_request_cb)

        self.library_cache = {}

        self.backend = AudioService()
        self.backend.player.connect_to_signal('state_changed', self.state_changed_cb)

        collection = self.backend.collection.query()

        for artist, albums in collection.iteritems():
            artist_iter = self.interface.add_artist(artist)
            for album, tracks in albums.iteritems():
                album_iter = self.interface.add_album(album, artist_iter)


    def state_changed_cb(self, data):

        self.interface.set_state(data['state'])

        if data['state'] != STATE_NULL:
            track = self.backend.collection.query({'_id': data['track']}).items()[0][1].items()[0][1].items()[0][1]
    
            position_rel = float(data['position']) / float(track['duration'])
            self.interface.display.set_position(position_rel)
    
            try:
                self.interface.display.set_title('{0} - {1} ({2})'.format(track['artist'], track['title'], track['album']))
            except:
                pass


    def interface_tracks_request_cb(self, source, query):
        self.interface.set_tracks(self.backend.collection.query(query))


    def interface_play_request_cb(self, source, id):

        if id:
            self.backend.player.set_track(id)
        self.backend.player.play()


    def interface_pause_request_cb(self, source):

        self.backend.player.pause()


AudioPlayer()
gtk.main()
