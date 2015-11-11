import functools
import tornado.options


def define_options(option_parser):
    # Debugging
    option_parser.define(
        'debug', default=False, type=bool, help="Turn on atuoreload and log to stderr",
        callback=functools.partial(enable_debug, option_parser),
        group="Debugging")

    def config_callback(path):
        option_parser.parse_config_file(path, final=False)

    option_parser.define(
        "config", type=str, help="Path to config file",
        callback=config_callback, group='Config file')

    # Application
    option_parser.define(
        'autoreload', type=bool, default=False, group='Application')

    option_parser.define('cookie_secret', type=str, group='Application')
    option_parser.define(
        'port', default=8888, type=int, help=('Server port'), group='Application')

    option_parser.define(
        'theme',default='theme',type=str,help=('Directory name of your theme files'),group='Appearance'
      )

    # Identify
    option_parser.define('host',default='localhost',type=str,help=('Server hostname'),group='Identity')
    option_parser.define('blog_name',type=str,help=('Display name for the site'),group='Identity')
    option_parser.define('base_url',type=str,help=('Base url,e.g."blog"'),group='Identity')

    # Admin
    option_parser.define('user',type=str,group='Admin')
    option_parser.define('password',type=str,group='Admin')

    # Appearance
    option_parser.define('timezone',type=str,default='Asia/Harbin',help='Your timezone name',group='Appearance')

    option_parser.add_parse_callback(functools.partial(check_required_options,option_parser))

    #TODO more options

def check_required_options(option_parser):
  for required_option_name in ('host','port','blog_name','base_url','cookie_secret','timezone',):
    if not getattr(option_parser,required_option_name,None):
      message=('%s required.(Did you forget to pass "--config=CONFIG_FILE"?)' % (required_option_name))
      raise tornado.options.Error(message)

def enable_debug(option_parser,debug):
  if debug:
    option_parser.log_to_stderr = True
    option_parser.autoreload = True



