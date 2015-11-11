"""Implementation of metaWeblog XML-RPC interface.

  See http://xmlrpc.scripting.com/metaWeblogApi.html
"""

import xmlrpclib

from tornadorpc.xml import XMLRPCHandler,XMLRPCParser
from roll_blog.api import posts,media,categories,tags


__all__ = (
  'APIHandler',
  )

class WordpressParser(XMLRPCParser):
  """Special parsing.

  Dispatches names like 'wp.getRecentPosts' to wp_getRecentPosts().
  """
  def parse_request(self,request_body):
    result = super(WordpressParser,self).parse_request(request_body)
    if isinstance(result,xmlrpclib.Fault):
      raise result
    else:
      ((method_name,params),) = result
      return ((method_name.replace('.','_'),params),)

class APIHandler(
  XMLRPCHandler,posts.Posts,media.Media,categories.Categories,tags.Tags):
  _RPC_ = WordpressParser(xmlrpclib)

  def mt_supportedTextFilters(self):
    return [
      {'key':'markdown','label':'Markdown'},
    ]
