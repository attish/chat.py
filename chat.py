#!/usr/bin/env python

import web as webpy
import threading
import time
import datetime
import random

# messages is the list of message lines. thread_lock is a dict that
# assigns locks to waiting threads. session_pos is a dict that assigns
# their current position in the message list to sessions.
messages = []
thread_lock = {}
session_pos = {}

urls = (
    '/([0-9]+)', 'Read',
    '/', 'KeepReading',
    '/say', 'Say',
    '/chat', 'Frame',
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

class KeepReading:
    def GET(self):
        webpy.header('Content-type', 'text/html')
        thread_id = str(threading.current_thread())
        pos = 0
        while True:
            if pos == len(messages):
                thread_lock[thread_id] = threading.Event()
                thread_lock[thread_id].clear()
                thread_lock[thread_id].wait()
            yield messages[pos] + '\n'
            pos += 1

class Say:
    def GET(self):
        line = webpy.input()['l']
        messages.append(line)
        for thread in thread_lock:
            thread_lock[thread].set()
        return "Line '%s' accepted." % line

class Frame:
    def GET(self):
        input = webpy.input()
        if 'l' in input:
            line = input['l']
            messages.append(line)
            for thread in thread_lock:
                thread_lock[thread].set()
        randnum = random.randint(0, 2000000000)
        page = """
        <html>
            <head>
                <title>Minimal web chat</title>
                <script type="text/javascript" src="static/jquery.js"></script>
            </head>
            <body>
                <div id="chat"></div>
                    <input id="text">
                    </input>
                    <input type="button" value="Send" onclick="sendMsg()">
                    </input>
                </form>
                <script type="text/javascript">
                    function sendMsg() {
                        var msg = $('#text').val();
                        $.get('/say?l=' + escape(msg));
                    }

                    function getMsg() {
                        $.ajax({
                            url: '/%d',
                            dataType: 'text',
                            type: 'get',
                            success: function(line) {
                                $('#chat').append('<p>' + line + '</p>');
                                setTimeout('getMsg()', 1000);
                                }
                        });
                    }
                    getMsg();
                </script>
            </body>
        </html>
        """
        return page % randnum

if __name__ == '__main__':
    webapp = webpy.application(urls, globals())
    webapp.run()
