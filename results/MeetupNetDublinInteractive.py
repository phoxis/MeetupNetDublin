#!/usr/bin/python3

import http.server
import socketserver
import webbrowser
import sys
import time
import os
import threading

#port = 8000;
#Handler = http.server.SimpleHTTPRequestHandler;
#httpd = socketserver.TCPServer(("", port), Handler);
#print ("Port: ", port);

target_file = {"mono": "meetup_dublin_mono.gexf", "community": "meetup_dublin_comm.gexf"}
option = "mono";

if len (sys.argv) > 1:
  option = sys.argv[1];
  if option not in target_file:
    option = "mono";
    print ("Invalid option \"{}\", Valid options: \"mono\", \"community\". Falling  back to default: \"mono\"", sys.argv[1]);

#pid = os.fork ();
#if pid == 0:
  #webbrowser.open("http://0.0.0.0:8000/MeetupNetDublinInteractive/index.html#" + target_file[option], new = 1);
#elif pid == -1:
  #print ("Fork failed");
#else:
  #httpd.serve_forever();

def start_server ():
  port = 8000;
  Handler = http.server.SimpleHTTPRequestHandler;
  httpd = socketserver.TCPServer(("", port), Handler);
  print ("Port: ", port);
  httpd.serve_forever();

t = threading.Thread (target = start_server);
t.start();
webbrowser.open("http://0.0.0.0:8000/MeetupNetDublinInteractive/index.html#" + target_file[option], new = 1);



while True:
  try:
    time.sleep(1)
  except KeyboardInterrupt:
    sys.exit(0)


