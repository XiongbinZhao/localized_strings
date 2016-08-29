
from __future__ import absolute_import
import codecs, re, chardet

format_encoding = 'UTF-16'

def _unescape_key(s):
	return s.replace('\\\n', '')

def _unescape(s):
	s = s.replace('\\\n', '')
	return s.replace('\\"', '"').replace(r'\n', '\n').replace(r'\r', '\r')

def _get_content(filename=None, content=None):
  if content is not None:
      if chardet.detect(content)['encoding'].startswith(format_encoding):
          encoding = format_encoding
      else:
          encoding = 'UTF-8'
      if isinstance(content, str):
          content.decode(encoding)
      else:
          return content
  if filename is None:
      return None
  return _get_content_from_file(filename, format_encoding)

def _get_content_from_file(filename, encoding):
  f = open(filename, 'r')
  try:
      content = f.read()
      if chardet.detect(content)['encoding'].startswith(format_encoding):
          #f = f.decode(format_encoding)
          encoding = format_encoding
      else:
          #f = f.decode(default_encoding)
          encoding = 'utf-8'
      f.close()
      f = codecs.open(filename, 'r', encoding=encoding)
      return f.read()
  except IOError, e:
      print "Error opening file %s with encoding %s: %s" %\
              (filename, format_encoding, e.message)
  except Exception, e:
      print "Unhandled exception: %s" % e.message
  finally:
      f.close()

def parse_strings(content="", filename=None):
  if filename is not None:
    content = _get_content(filename=filename)

  stringset = []
  f = content
  if f.startswith(u'\ufeff'):
      f = f.lstrip(u'\ufeff')
  
  cp = r'(?:/\*(?P<comment>(?:[^*]|(?:\*+[^*/]))*\**)\*/)'
  kv = r'(?://+){0,1}\s*(?P<line>(?:"(?P<key>[^"\\]*)")\s*=\s*(?:"(?P<value>[^"\\]*)"\s*;))'

  strings = r'(?:%s[ \t]*[\n]|[\r\n]|[\r]){0,1}%s'%(cp, kv)
  p = re.compile(strings)
  for r in p.finditer(f):
  	key = r.group('key')
  	value = r.group('value')
  	comment = r.group('comment') or ''
  	key = _unescape_key(key)
  	value = _unescape(value)
  	stringset.append({'key': key, 'value': value, 'comment': comment})
  	return stringset

strings_b = parse_strings(filename = 'CouponAllLoadedView.strings')


















