#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Chris Lin
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
       
        #check http in url 
        if ("http://") not in url:
            url = "http://"+url
        #should return something like
        #ParseResult(scheme='http', netloc='example.com', path='/index.php'....etc)
        info = urlparse(url)
        host = info.hostname
        if info.port != None:
            port = info.port
        else:
            port = 80
        path = info.path
   
        print "get host port is",host,port,path
        return host,port,path

    def connect(self, host, port):
        # use sockets!
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            port = int(port)
            client.connect((host,port))
        except socket.timeout:
            print "Fail to connect to socket"
            
        return client

    def get_code(self, data):
        status_code = int(data.split()[1])
        return status_code

    def get_headers(self,data):
        info = data.split('\r\n\r\n')[0]
        return info[0]

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    
    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)
                
            
    def GET(self, url, args=None):
        code = 500
        body = ""
        host,port,path = self.get_host_port(url)
        #print host, port, path
        client = self.connect(host,port)
        request = "GET "+path+" HTTP/1.1\r\nHost: " +host+ "\r\n\r\n"
        print "checking rquest",request
        client.sendall(request)
        read_data = self.recvall(client)
        code = self.get_code(read_data)
        print "get code",code
        body = self.get_body(read_data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        encode = ""
        host,port,path = self.get_host_port(url)
        if args != None:
            encode = urllib.urlencode(args)
        request = "POST " + path + " HTTP/1.1\r\n"\
                  "Host: "+ host + "\r\n"\
                  "Content-Type: application/x-www-form-urlencoded;charset=utf-8\r\n"\
                  "Content-Length: " + str(len(encode)) +"\r\n\r\n"+ encode
        print "checking rquest",request
        client = self.connect(host,port)
        client.sendall(request)
        read_data = self.recvall(client)
        code = self.get_code(read_data)
        
        body = self.get_body(read_data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
