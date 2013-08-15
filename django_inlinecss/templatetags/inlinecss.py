from django import template

from django.utils.encoding import smart_unicode

from django_inlinecss import conf

register = template.Library()

def full_path(path):
    try:
        from django.contrib.staticfiles.storage import staticfiles_storage
        return staticfiles_storage.path(path)
    except ImportError:
        from django.conf import settings
        import os
        return os.path.join(settings.MEDIA_ROOT, path)

class InlineCssNode(template.Node):
    def __init__(self, nodelist, filter_expressions):
        self.nodelist = nodelist
        self.filter_expressions = filter_expressions

    def render(self, context):
        rendered_contents = self.nodelist.render(context)
        css = ''
        for expression in self.filter_expressions:
            path = expression.resolve(context, True)
            if path is not None:
                path = smart_unicode(path)
            expanded_path = full_path(path)

            with open(expanded_path) as css_file:
                css = ''.join((css, css_file.read()))

        engine = conf.get_engine()(html=rendered_contents, css=css)
        return engine.render()


@register.tag
def inlinecss(parser, token):
    nodelist = parser.parse(('endinlinecss',))

    # prevent second parsing of endinlinecss
    parser.delete_first_token()

    args = token.split_contents()[1:]

    return InlineCssNode(
        nodelist,
        [parser.compile_filter(arg) for arg in args])
