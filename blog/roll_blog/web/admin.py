import datetime
import json
import logging
from urllib import urlencode

import tornado.web
from tornado import gen
from tornado.options import options as opts

from roll_blog.web.handlers import RollBlogHandler

__all__ = (
    'LoginHandler',
  )

class LoginHandler(RollBlogHandler):
  """Authenticate as the administrator."""
  @tornado.web.addslash
  def get(self):
    if self.current_user:
      self.write('already login')
    else:
      #next_url = self.get_argument('next',None)
      self.render('admin-templates/login.html',
        error=None)

  def post(self):
    user = self.get_argument('user')
    password = self.get_argument('password')
    #next_url = self.get_argument('next',None)
    if user == opts.user and password == opts.password:
      self.set_secure_cookie('auth',user)
      #self.redirect(next_url or self.reverse_url('drafts'))
      self.write('login success')
      return
    else:
      error="Incorrect username or password,check roll_blog.conf"
      self.render('admin-templates/login.html',
        error=error)
