from django import template
from ..models import Snippet

register = template.Library()

class snippet_node(template.Node):
	def __init__(self, name, default):
		self.name = template.Variable(name)
		if default:
			self.default = template.Variable(default)
		else:
			self.default = None
	
	def render(self, context):
		name = self.name.resolve(context)
		try:
			snippet = Snippet.objects.get(name=name)
		except Snippet.DoesNotExist:
			if self.default:
				default = self.default.resolve(context)
			else:
				default = "New Snippet"
			snippet = Snippet.objects.create(name=name, content=default)
			snippet.save()
		return snippet.content
		
@register.tag
def snippet(parser, token):
	args = token.split_contents()
	if len(args) > 3:
		raise template.TemplateSyntaxError("Snippet takes at most two arguments")
	if len(args) > 2:
		default = args[2]
	else:
		default = None
	name = args[1]
	return snippet_node(name, default)

class snippet_block_node(template.Node):
	def __init__(self, nodelist, name):
		self.name = template.Variable(name)
		self.nodelist = nodelist
	
	def render(self, context):
		name = self.name.resolve(context)
		try:
			snippet = Snippet.objects.get(name=name)
		except Snippet.DoesNotExist:
			default = self.nodelist.render(context)
			snippet = Snippet.objects.create(name=name, content=default)
			snippet.save()
		return snippet.content

@register.tag
def snippetblock(parser, token):
	args = token.split_contents()
	if len(args) != 2:
		raise template.TemplateSyntaxError("Snippetblock takes two arguments")
	name = args[1]
	nodelist = parser.parse(('endsnippetblock',))
	parser.delete_first_token()
	return snippet_block_node(nodelist, name)

