from django import template
from django.utils.html import escape

register = template.Library()


@register.tag(name="render_js")
def do_render_js(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, variable_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly one argument" % token.contents.split()[0]
        )
    if not (variable_name[0] == variable_name[-1] and variable_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )

    nodelist = parser.parse(('endrenderjs',))
    parser.delete_first_token()
    return RenderJS(nodelist, variable_name=variable_name[1:-1])


class RenderJS(template.Node):
    def __init__(self, nodelist, variable_name):
        self.nodelist = nodelist
        self.variable_name = variable_name

    def render(self, context):
        output = self.nodelist.render(context)
        content = escape(output)
        return f"<script>window.{self.variable_name} = `{content}`;</script>\n"
