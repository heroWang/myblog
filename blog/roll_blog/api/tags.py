from roll_blog.api import coroutine, rpc


class Tags(object):
    """Handle XML-RPC calls related to tags.

    Mixin for motor_blog.api.handlers.APIHandler.
    """
    @rpc
    @coroutine
    def wp_getTags(self, blogid, user, password):
      # not needed for my blog at present
      self.result([])
