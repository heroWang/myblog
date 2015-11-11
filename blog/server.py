#!/usr/bin/env python
from functools import partial
import logging
import os

import motor
import tornado.ioloop
import tornado.web
from tornado.options import options as opts
from tornado import httpserver

#Patch Tornado with the Jade template loader
from tornado import template
from pyjade.ext.tornado import patch_tornado
from roll_blog.options import define_options

patch_tornado()

from roll_blog import application

if __name__ == '__main__':
  define_options(opts)
  opts.parse_command_line()
  for handler in logging.getLogger().handlers:
    if hasattr(handler,'baseFilename'):
      print 'Logging to', handler.baseFilename
      break

  # TODO:cache , indexes prepare
  db = motor.MotorClient().rollblog
  loop=tornado.ioloop.IOLoop.current()
  #loop.run_sync(partial(cache.startup,db))

  this_dir=os.path.dirname(__file__)#get current dir path
  application = application.get_application(this_dir,db,opts)
  http_server = httpserver.HTTPServer(application,xheaders=True)
  http_server.listen(opts.port)

  msg = 'Listening on port %s' % opts.port
  print msg
  logging.info(msg)

  #start event loop
  loop.start()


