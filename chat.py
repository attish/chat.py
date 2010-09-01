#!/usr/bin/env python

import web as webpy
import threading
import time
import datetime

# messages is the list of message lines. thread_lock is a dict that
# assigns locks to waiting threads. session_pos is a dict that assigns
# their current position in the message list to sessions.
messages = []
thread_lock = {}
session_pos = {}

urls = (
    '/([0-9]+)', 'Read',
    '/say/(.*)', 'Say',
    )

class Read:
    def GET(self, session_id):
        webpy.header('Content-type', 'text/html')
        thread_id = str(threading.current_thread())
        if session_id not in session_pos:
            session_pos[session_id] = 0
        pos = session_pos[session_id]
        if pos == len(messages):
            thread_lock[thread_id] = threading.Event()
            thread_lock[thread_id].clear()
            thread_lock[thread_id].wait()
        yield messages[pos] + '\n'
        session_pos[session_id] += 1

class Say:
    def GET(self, line):
        messages.append(line)
        for thread in thread_lock:
            thread_lock[thread].set()
        return "Line '%s' accepted." % line

if __name__ == '__main__':
    webapp = webpy.application(urls, globals())
    webapp.run()
