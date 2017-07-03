import socket
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop


""" Sockets array to send websocket messages """
sockets = []


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Websocket
    """
    def open(self):
        print("Websocket: open")
        sockets.append(self)

    def on_close(self):
        print("Websocket: on_close")
        sockets.remove(self)

    def data_received(self, chunk):
        print("Websocket: data_received")

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        print("Websocket: receive: %s" % message)
        if message == 'ping':
            answer = 'pong'
        else:
            answer = 'Hello World!'

        print("Websocket: send: %s" % answer)
        self.write_message(answer)


class HttpHandler(tornado.web.RequestHandler):
    """
    Http
    """
    def data_received(self, chunk):
        print("HttpHandler: data_received")

    def post(self):
        print("HttpHandler: a message has just been posted or deleted")
        self.write('success')

        event = self.get_argument('event')
        if event != 'create' and event != 'delete':
            event = 'unknown'

        print("HttpHandler: will notify %s user(s)" % len(sockets))
        for s in sockets:
            s.write_message("message_update_%s" % event)


application = tornado.web.Application([
    (r'/ws', WebSocketHandler),
    (r'/message_update', HttpHandler),
])


if __name__ == "__main__":
    port = 1234
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)

    ip = socket.gethostbyname(socket.gethostname())
    print('*** Tornado Websocket Server Started at %s:%s ***' % (ip, port))
    tornado.ioloop.IOLoop.instance().start()
