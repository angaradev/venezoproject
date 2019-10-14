from django import template
from django.core.files.storage import default_storage
from ecommerce.settings import POLAND_ZLOTY, DISCOUNT
import os
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter
import http.client as h
from urllib.parse import urlparse


register = template.Library()


@register.filter(name='check_image_exist')
def check_image_exist(value, arg):
    if not os.path.isfile(os.path.join('/home/manhee/anaconda3/envs/djecommerce/src/my_static/img', 'prod_thumbs', str(arg)) + '.webp'):
        return False
    else:
        return True


@register.filter(name='check_url_exist')
def check_url_exist(value):
    parse_object = urlparse(value)
    conn = h.HTTPConnection(parse_object.netloc, timeout=1)
    conn.request("HEAD", parse_object.path)
    res = conn.getresponse()
    if res.status == 200:
        return True
    else:
        return False

@register.filter(name='convert_price')
def convert_price(value):
    price = value * POLAND_ZLOTY
    price = "{:,}".format(price).replace(',', ' ')
    return price

@register.filter(name='old_price')
def old_price(value):
    price = round((value + value * DISCOUNT) * POLAND_ZLOTY)
    price = "{:,}".format(price).replace(',', ' ')
    return price



@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):

    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.filter
@stringfilter
def split_facet_first(value, splitter='|', autoescape=None):
    if not isinstance(value, SafeData):
        value = mark_safe(value)
    value = value.split(splitter)
    return mark_safe(value[0])
split_facet_first.is_safe = True
split_facet_first.needs_autoescape = True

@register.filter
@stringfilter
def split_facet_second(value, splitter='|', autoescape=None):
    if not isinstance(value, SafeData):
        value = mark_safe(value)
    value = value.split(splitter)
    return mark_safe(value[1])
split_facet_second.is_safe = True
split_facet_second.needs_autoescape = True