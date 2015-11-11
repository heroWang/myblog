import datetime
import time
import math

import tornado.web
from tornado import gen

from motor.web import GridFSHandler
import motor

from roll_blog.text.link import absolute
from roll_blog.models import *

ceil_div = lambda x,y : int(math.ceil(float(x) / y))

class RollBlogHandler(tornado.web.RequestHandler):
  def __init__(self,*args,**kwargs):
    super(RollBlogHandler,self).__init__(*args,**kwargs)
    self._last_modified = None

  def get_template_namespace(self):
    ns = super(RollBlogHandler,self).get_template_namespace()

    def get_setting(setting_name):
      return self.application.settings[setting_name]

    ns.update({
      'q':'',
      'setting':get_setting,
      'absolute':absolute
      })

    return ns

  def get_current_user(self):
    """Logged-in username or None"""
    return self.get_secure_cookie('auth')

  @gen.coroutine
  def render_async(self,template_name,**kwargs):
    """
    Since widgets may need to do I/O,this must be async and its result
    s yielded before the caller completes.
    """
    html =super(RollBlogHandler,self).render_string(template_name,**kwargs)
    #TODO somthing puzzle me
    self.finish(html)

  @gen.coroutine
  def get_posts(self,query,fields,sort,skip,limit):
    collection = self.settings['db'].posts
    cursor = collection.find(query,fields).sort(sort).skip(skip)
    docs = yield cursor.limit(limit).to_list(limit)
    posts = [Post(**doc) for doc in docs]
    raise gen.Return(posts)

class PostHandler(RollBlogHandler):
  """Show a shingle blog post or page, by slug."""
  @tornado.web.addslash
  @gen.coroutine
  def get(self,slug):
    slug = slug.rstrip('/')
    posts = self.settings['db'].posts
    post_doc = yield posts.find_one(
      {'slug':slug,'status':'publish'},
      {'summary':False,'original':False})

    if not post_doc:
      raise tornado.web.HTTPError(404)

    if post_doc['type'] == 'redirect':
      # This redirect marks where a real post or page used to be.
      url = self.reverse_url('post',post_doc['redirect'])
      self.redirect(url,permanent=True)
      return

    post = Post(**post_doc)

    #Only posts have prev / next navigation, not pages.
    if post.type == 'post':
      fields = {'summary':False, 'body':False, 'original':False}
      prev_doc_future = posts.find_one(
        {'status':'publish','type':'post','pub_date':{'$lt':post.pub_date}},
        fields,
        sort=[('pub_date',-1)]
        )

      next_doc_future = posts.find_one(
        {'status':'publish','type':'post','pub_date':{'$gt':post.pub_date}},
        fields,
        sort=[('pub_date',1)]
        )
      # Overkill for this case, but in theory we reduce latency by
      # querying for previous and next posts at onece, and waiting for
      # both.
      prev_doc,next_doc = yield [prev_doc_future, next_doc_future]
    else:
      prev_doc,next_doc = None, None

    prev_post = Post(**prev_doc) if prev_doc else None
    next_post = Post(**next_doc) if next_doc else None
    #categories = yield self.get_categories()
    yield self.render_async(
      'single.jade',
      post=post,
      prev=prev_post,
      next=next_post
      #categories=categories
      )
    print 'response end'

class MediaHandler(RollBlogHandler,GridFSHandler):
  @gen.coroutine
  def get(self, path):
    pass



class AllPostsHandler(RollBlogHandler):
  @tornado.web.addslash
  @gen.coroutine
  def get(self,page_num=1):
    single_page_posts_count=10

    collection = self.settings['db'].posts
    total_num_future=collection.find(
      {'status':'publish','type':'post'}
      ).count()

    total_num = yield total_num_future
    total_page_count = ceil_div(total_num , single_page_posts_count)

    posts = yield self.get_posts(
      {'status':'publish','type':'post'},
      {'original':False},
      [('pub_date',-1)],
      (int(page_num)-1)*single_page_posts_count,
      single_page_posts_count)

    yield self.render_async(
      'all-posts.jade',
      posts=posts,
      page_num=int(page_num),
      total_page_count=total_page_count)

class CategoryHandler(RollBlogHandler):
  @tornado.web.addslash
  @gen.coroutine
  def get(self,slug):
    slug = slug.rstrip('/')
    # TODO




