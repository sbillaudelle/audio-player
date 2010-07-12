#!/usr/bin/env python

import cream.ipc

class AudioService(object):

    def __init__(self):

        self.collection = AudioCollection()
        self.player = cream.ipc.get_object('org.cream.media', 
                                  '/org/cream/Media/Audio/Player')


class AudioCollection(object):

    def __init__(self):
        self.service = cream.ipc.get_object('org.cream.media', 
                                  '/org/cream/Media/Audio/Collection')

    def update_library(self, path):
        self.service.update_library(path)

    def query(self, query={}, ignorecase=False):
        return self.service.query(query, ignorecase)

    def update_or_add(self, track):
        self.service.update_or_add(track)

    def remove_track(self, _id):
        self.service.remove_track(_id)
