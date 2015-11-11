# coding:utf-8

import datetime

from bson.objectid import ObjectId
from dictshield.document import Document,EmbeddedDocument
from dictshield.fields import StringField,IntField,DateTimeField
from dictshield.fields.compound import SortedListField,EmbeddedDocumentField,ListField
from dictshield.fields.mongo import ObjectIdField

from roll_blog.text.link import absolute

import pytz
from roll_blog.text import summarize,slugify,plain,markup

utc_tz = pytz.timezone('UTC')


class BlogDocument(Document):
  @property
  def date_created(self):
    """datetime when this posts was created, timezone-aware in UTC"""
    return self.id.generation_time

  class Meta:
    id_field =ObjectIdField

class Category(BlogDocument):
  name = StringField()
  slug = StringField()

  @classmethod
  def _from_rpc(cls,struct,name):
    _id = ObjectId(struct['categoryId']) if 'categoryId' in struct else None

    return cls(name=name,slug=slugify.slugify(name),id=_id)

  @classmethod
  def from_metaweblog(cls,struct):
    name = struct['categoryName']
    return cls._from_rpc(struct,name)

  def to_wordpress(self,application):
    url = absolute(application.reverse_url('category',self.slug))
    return {
      'categoryId': str(self.id),
      'categoryName': self.name,
      'htmlUrl': url,
      'rssUrl': url,
    }

  # alias of to_wordpress
  to_metaweblog = to_wordpress

  @property
  def last_modified(self):
    return self.date_created

class EmbeddedCategory(Category,EmbeddedDocument):
  pass



class Post(BlogDocument):
  """A post or a page"""
  title = StringField(default='')
  # Formatted for display.
  body = StringField(default='')
  # Input from MarsEdit or migrate_from_wordpress
  original = StringField(default='')
  # Plain text.
  plain = StringField(default='')
  # Plain-text excerpt
  summary = StringField(default='')
  author = StringField(default='')
  type = StringField(choices=('post','page','redirect'),default='post')
  status = StringField(choices=('publish','draft'),default='publish')
  meta_description = StringField(default='')
  tags = SortedListField(StringField())
  categories = SortedListField(EmbeddedDocumentField(EmbeddedCategory))
  slug = StringField(default='')
  #guest_access_tokens = ListField(EmbeddedDocumentField(GuestAccessToken))
  wordpress_id = IntField() #legacy id from WordPress
  pub_date = DateTimeField()
  mod = DateTimeField()
  # Post was moved, this is its new slug.
  redirect = StringField(default = None)

  def __init__(self,*args,**kwargs):
    super(Post,self).__init__(*args,**kwargs)
    if not self.mod.tzinfo:
      self.mod = utc_tz.localize(self.mod)

  @classmethod
  def from_metaweblog(cls,struct,post_type='post',is_edit=False):
    """Receive metaWeblog RPC struct and initialize a Post.
        Used both by migrate_from_wordpress and when receiving a new or
        edited post from MarsEdit.
    """
    title = struct.get('title','')
    meta_description = struct.get('mt_excerpt','')
    if len(meta_description) > 155:
      raise ValueError(
        "Description is %d chars, max 155" % len(meta_description))

    if 'mt_keywords' in struct:
      tags = [
        tag.strip() for tag in struct['mt_keywords'].split(',')
        if tag.strip()]
    else:
      tags = None

    slug = (
      slugify.slugify(struct['wp_slug'])
      if struct.get('wp_slug')
      else slugify.slugify(title))

    print struct.get('wp_slug') , slugify.slugify(title)

    description = struct.get('description','')
    status = (struct.get('post_status')
        or struct.get('page_status')
        or 'publish')

    if 'date_modified_gmt' in struct:
      tup = struct['date_modified_gmt'].timetuple()
      mod = utc_tz.localize(datetime.datetime(*tup[0:6]))
    else:
      mod = datetime.datetime.utcnow()

    body = markup.markup(description)

    rv = cls(
      title=title,
      #Format for display
      body=body,
      plain=plain.plain(body),
      summary=summarize.summarize(body,200),
      original=description,
      meta_description=meta_description,
      tags=tags,
      slug=slug,
      type=post_type,
      status=status,
      wordpress_id=struct.get('postid'),
      mod=mod
      )

    if not is_edit and 'date_created_gmt' in struct:
      #TODO: can fail if two posts created in same second,add random suffix to ObjectId
      date_created = datetime.datetime.strptime(
        struct['date_created_gmt'].value,'%Y%m%dT%H:%M:%S')
      rv.id = ObjectId.from_datetime(date_created)

    return rv


  def to_python(self):
    dct =super(Post,self).to_python()

    if 'id' in dct:
      dct['_id'] = dct.pop('id')

    return dct

  def to_metaweblog(self,application):
    # kind of throwing fieldnames at the wall and see what sticks,
    # MarsEdit expects different names in the responses to different API calls

    if self.status=='publish':
      url = absolute(application.reverse_url('post',self.slug))
    else:
      url = absolute(application.reverse_url('draft',self.slug))

    rv = {
      'title':self.title,
      # Note we're returning the original, not the display version
      'description': self.original,
      'link': url,
      'permaLink': url,
      #'categories':
      'mt_keywords': ','.join(self['tags']),
      'dateCreated': self.local_date_created(application),
      'date_created_gmt': self.date_created,
      'postid':str(self.id),
      'status':self.status,
      'wp_slug':self.slug,
      'mt_excerpt':self.meta_description,
      'id':str(self.id)
    }


    if self.type =='post':
      rv['post_id'] = str(self.id)
      rv['post_status'] = self.status
    elif self.type == 'page':
      rv['page_id'] = str(self.id)
      rv['page_status'] = self.status

    return rv

  @property
  def date_created(self):
    if self.pub_date:
      return utc_tz.localize(self.pub_date)
    else:
      return super(Post,self).date_created

  @property
  def local_short_date(self):
    dc=self.date_created
    return '%s年%s月%s日' %(dc.year,dc.month,dc.day)


  def local_date_created(self,application):
    dc = self.date_created
    tz = application.settings['tz']
    return tz.normalize(dc.astimezone(tz))

  @property
  def display_summary(self):
    return self.meta_description if self.meta_description else self.summary
