"""Convert Markdown to HTML."""

import markdown
import pygments

#from roll_blog.text import markdown_widget_extension

__all__ =('markup',)

def markup(text):
  return markdown.markdown(text,extensions=[
    'codehilite(linenums=False,noclasses=False)','fenced_code','extra',
    'toc'
    ])
