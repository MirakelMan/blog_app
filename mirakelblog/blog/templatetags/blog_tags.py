from django import template

from ..models import Post

# Each module that contains template tags needs to define
# a variable called register to be a valid tag library.
register = template.Library()


# If you want to register it using a different name,
# you can do so by specifying a name attribute,
# such as @register.simple_tag(name='my_tag')
@register.simple_tag
def total_posts():
    return Post.published.count()
