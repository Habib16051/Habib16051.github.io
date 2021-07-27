# -*- coding: utf-8 -*-

from django.template import Library
from django.conf import settings
import os
import os.path
import subprocess

yui_jar_root = os.path.dirname(
  os.path.dirname(os.path.abspath(__file__)))

yui_jar_path = os.path.join(yui_jar_root,
                            "yuicompressor-2.4.2.jar")

register = Library()


def yui_files(filenames, bundle_name, folder, ext):
  if settings.DEBUG:
    return [settings.MEDIA_URL + folder + "/" + \
              filename + "." + ext
            for filename in filenames.split(":")]
  filenames = [os.path.join(settings.MEDIA_ROOT,
                            folder,
                            filename + "." + ext)
               for filename in filenames.split(":")]
  m_times = [int(os.stat(filename).st_mtime)
             for filename in filenames]
  hash_key = sum(m_times)
  bundle_name = os.path.join(
    settings.MEDIA_ROOT, folder,
    settings.YUI_BUNDLE_NAME + str(hash_key) + "." + ext)
  if not os.path.isfile(bundle_name):
    merged_filename = os.tempnam()
    out_filename = os.tempnam()
    with open(merged_filename, "w") as out:
      for filename in filenames:
        with open(filename) as inp:
          out.write(inp.read())
    yui = subprocess.Popen(["java", "-jar", yui_jar_path, "--type", ext,
                            "-o", out_filename, merged_filename])
    yui.wait()
    with open(bundle_name, "w") as out:
      with open(out_filename) as inp:
        out.write(inp.read())
    os.unlink(out_filename)
    os.unlink(merged_filename)
  return [settings.MEDIA_URL + folder + "/" + \
            settings.YUI_BUNDLE_NAME + str(hash_key) + "." + ext]


@register.simple_tag
def yui_js(filenames):
  out = []
  for link in yui_files(filenames, settings.YUI_BUNDLE_NAME,
                        settings.YUI_JS_FOLDER, "js"):
    out.append("<script type=\"text/javascript\" src=\"%s\">"
               "</script>" % link)
  return "\n".join(out)


@register.simple_tag
def yui_css(filenames):
  out = []
  for link in yui_files(filenames, settings.YUI_BUNDLE_NAME,
                        settings.YUI_CSS_FOLDER, "css"):
    out.append("<link rel=\"stylesheet\" type=\"text/css\""
               " href=\"%s\" />" % link)
  return "\n".join(out)


