import datetime
import xmlrpclib

from bson.objectid import ObjectId

#from roll_blog import cache
from roll_blog.api import coroutine, rpc
from roll_blog.models import Post, Category #,EbeddedCategory

class Categories(object):
  @rpc
  @coroutine
  def wp_getCategories(self,blogid,user,password):
    #Could cache this as we do on the web side,but not worth the risk
    db = self.settings['db']
    categories = yield db.categories.find().sort(
      [('name',1)]).to_list(100)

    self.result([Category(**c).to_wordpress(self.application)
      for c in categories])

  @rpc
  @coroutine
  def mt_getPostCategories(self, postid, user, password):
    post = yield self.settings['db'].posts.find_one(ObjectId(postid))

    if not post:
      self.result(xmlrpclib.Fault(404,"Not Found"))
    else:
      self.result([cat.to_metaweblog(self.application)
        for cat in Post(**post).categories])

  @rpc
  @coroutine
  def wp_newCategory(self,blogid,user,password,struct):
    category = Category.from_wordpress(struct)
    _id = yield self.settings['db'].categories.insert(category.to_python())

    #TODO yield cache.event('categories_changed')
    self.result(str(_id))



