import base64
import json
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import urllib.parse as urlparse
from switchbot import Switchbot
import asyncio


class HTTPServer(TCPServer):
    daemon_threads = True
    key = None

    def set_auth(self, username, password):
        self.key = base64.b64encode(bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key


def load_file(file):
    with open(file, 'rb') as file_handler:
        return file_handler.read()


def serve_on_port(port, user, pwd):
    server = HTTPServer(('0.0.0.0', port), HTTPHandler)
    if user is not None and pwd is not None:
        server.set_auth(user, pwd)
    print("Serving at localhost:{}".format(port))
    server.serve_forever()


class HTTPHandler(BaseHTTPRequestHandler):

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="CC Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        key = self.server.get_auth_key()
        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') is None and key is not None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        elif self.headers.get('Authorization') == 'Basic ' + str(key) or key is None:
            query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            mac              = query_components.get('device', [None])[0]
            interface        = query_components.get('interface', [0])[0]
            connect_timeout  = query_components.get('connect_timeout', [5])[0]
            command_type     = query_components.get('command', '[]')[0]

            print ("device: {}, interface: {}, timeout: {}, command: {}".format(mac, interface, connect_timeout, command_type))

            choices=['press', 'on', 'off', 'status']

            if mac is None:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Device not found...')
            elif command_type in choices :
                bot = Switchbot(mac,None,interface,retry_count=3,scan_timeout=connect_timeout)
                result = 'OK'

                if command_type == 'on':
                    asyncio.run(bot.turn_on())
                elif command_type == 'off':
                    asyncio.run(bot.turn_off())
                elif command_type == 'press':
                    asyncio.run(bot.press())
                elif command_type == 'status':
                    asyncio.run(bot.update())
                    result = bot.is_on() and '1' or '0'
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(result, 'utf-8'))
            elif command_type == 'status':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Not yet supported')
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Command not found...')


# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--user", default=None, help="Username")
parser.add_argument("-pwd", "--password", default=None, help="Password")
parser.add_argument("-p", "--port", default=8080, type=int, help="Port")
args = vars(parser.parse_args())

PORT = args["port"]
USER = args["user"]
PWD = args["password"]

if __name__ == '__main__':
    serve_on_port(PORT, USER, PWD)