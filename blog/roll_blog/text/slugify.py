#import re
import logging
import uuslug
#from unicodedata import normalize

# From http://flask.pocoo.org/snippets/5/
# Wordpress's slugs.
#_punct_re = re.compile(r'[\t !#$%&\()*\-/<=>?@\[\\\]^_`{|},:.+]+')

# def slugify(text,delim=u'-'):
#   logging.info("slugify %s" % (text))
#   result = []
#   # Strip quotes.
#   text = text.replace("'",'').replace('"','')
#   for word in _punct_re.split(text.lower()):
#     word = normalize('NFKD',unicode(word)).encode('ascii','ignore')
#     if word:
#       result.append(word)

#   slug=unicode(delim.join(result))
#   logging.info("slugify result: %s" % slug)
#   return slug

def slugify(text):
  return uuslug.slugify(text)
