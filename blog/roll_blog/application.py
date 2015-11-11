import os
import pytz

#import sockjs.tornado
import tornado.web
from roll_blog.web import get_url_spec
from motor.web import GridFSHandler
from tornado.web import StaticFileHandler
from roll_blog.api.handlers import APIHandler
from roll_blog.web.handlers import *

from roll_blog.web.admin import *

def get_application(root_dir,db,option_parser):
  base_url = option_parser.base_url
  static_path = os.path.join(option_parser.theme,'static')
  #resource_path = os.path.join(root_dir,'ro_blog/resource')
  U = get_url_spec(base_url)

  urls = [
    #XML-RPC wordpress API
    U(r"/api",APIHandler,name="api"),
    U(r'page/(?P<page_num>\d+)/?',AllPostsHandler,name='page'),
    #Admin
    U(r'admin/?',LoginHandler,name='login'),
    U(r'theme/static/(.+)',StaticFileHandler,{"path":static_path}),
    U(r'media/(.+)', GridFSHandler,{'database':db},name='media'),
    U(r'category/(?P<slug>.+)/?',CategoryHandler,name='category'),
    # TODO more url mappings

    # must be last ,because this mapping could deal any url
    #U(r'/(?P<slug>.+)/?',PostHandler,name='post'),
  ]
  urls.append(U(r'/?',AllPostsHandler,name='home'))
  urls.append(U(r'/(?P<slug>.+)/?',PostHandler,name='post'))

  return tornado.web.Application(
      urls,
      tz=pytz.timezone(option_parser.timezone),
      template_path=os.path.join(option_parser.theme,'templates'),
      gzip=True,
      db=db,
      **{k:v.value() for k,v in option_parser._options.items()}
    )
