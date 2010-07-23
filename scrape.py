#!/usr/bin/python

usage_example = "%prog --output-dir=/tmp/path/example"

# mod_autoindex generated HTML containing builds:
index_url = "http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/"
parse_url = "http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/?C=M;O=D"

from optparse import OptionParser
import os
from sgmllib import SGMLParser
import shutil
import simplejson as json
import urllib2

path_to_this_script = os.path.realpath(__file__)

class BuildDisplay():
    def __init__(self, suffix, extension, name, css_class):
        self.suffix = suffix
        self.extension = extension
        self.name = name
        self.css_class = css_class

files_wanted = [
#               (suffix,                    extension, name,                  css_class)
    BuildDisplay(".win32.installer",        "exe",     "Windows",             "windows exe"),
    BuildDisplay(".win64-x86_64.installer", "exe",     "Windows 64-bit",      "windows exe x64"),
    BuildDisplay(".mac",                    "dmg",     "Mac",                 "mac dmg"),
    BuildDisplay(".mac64",                  "dmg",     "Mac 64-bit for 10.6", "mac dmg x64"),
    BuildDisplay(".linux-i686",             "tar.bz2", "Linux Intel",         "linux bz2"),
    BuildDisplay(".linux-x86_64",           "tar.bz2", "Linux 64-bit Intel",  "linux bz2 x64")
]

wanted_keys = tuple([f.suffix + "." + f.extension for f in files_wanted])

def build(url, files_wanted):
    d = {}
    d['url'] = index_url + url
    d['date'] = ""
    d['size'] = ""
    for f in files_wanted:
        if d['url'].endswith(f.suffix + "." + f.extension):
            d['css_class'] = f.css_class
            d['name'] = f.name
            d['extension'] = f.extension
            d['suffix'] = f.suffix
            return d

class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.builds = []
        self.textData = ""
            
    def start_td(self, attrs):
        self.textData = ""

    def end_td(self):
        text = self.textData.strip()

        if (self.textData.endswith(wanted_keys)):
            self.builds.append(build(text, files_wanted))
            return

        if (len(self.builds) > 0):
            if (self.builds[-1]['date'] == ""):
                self.builds[-1]['date'] = text.split()[0]
            elif (self.builds[-1]['size'] == ""):
                self.builds[-1]['size'] = text

    def handle_data(self, text):
        self.textData += text

def buildJSON(recent_builds):
    output = []
    for build in recent_builds:
        output.append(build)
    return json.dumps(output, indent=0)

def buildHTML(recent_builds):
    header = """<!DOCTYPE html>
<html>
      <head>
        <title>Firefox Nightly Builds</title>
        <link rel="stylesheet" type="text/css" href="http://www.mozilla.com/style/tignish/template.css" />
        <link rel="stylesheet" type="text/css" href="http://www.mozilla.com/style/tignish/content.css" />
        <link rel="stylesheet" type="text/css" href="nightly.css" />
      </head>
      <body>
        <div id="main-feature">
          <h1>Firefox Nightly Builds</h1>
          <p>These builds are for testing purposes only.</p>
        </div>
        <ul>\n"""
    
    footer = """
        </ul>
                
        <p>We have <a href="%s">more stuff</a> if you don't see what you're looking for.</p>

      </body>
</html>""" % parse_url
    
    middle = ""
    for build in recent_builds:
        middle += '\n<li class="' + build['css_class'] + '">\n'
        middle += '<a href="' + build['url'] + '">'
        middle += build['name']
        middle += '</a>'
        middle += ' ' + build['size'] + 'B'
        middle += '  ' + build['extension']
        middle += '<br>\n'
        middle += '<small>Built on ' + build['date'] + '</small>\n'

    return header + middle + footer

def writeOutput(output_dir, filename, text):
    f = open(os.path.join(output_dir, filename), 'w')
    f.write(text)
    f.close()

def copyFile(output_dir, fileName):
    resource_path = os.path.split(path_to_this_script)[0]
    shutil.copyfile(os.path.join(resource_path, fileName), os.path.join(output_dir, fileName))

def copyFileWithName(inputFile, output_dir, fileName):
    resource_path = os.path.split(path_to_this_script)[0]
    shutil.copyfile(os.path.join(resource_path, inputFile), os.path.join(output_dir, fileName))

def getRecentBuilds(builds):
    recent_builds_dict = {}
    for f in files_wanted:
        for build in builds:
            if build['url'].endswith(f.suffix + "." + f.extension) and f.css_class not in recent_builds_dict:
                recent_builds_dict[f.css_class] = build
    items = recent_builds_dict.items()
    items.sort()
    return [value for key, value in items]

def main():
    optparser = OptionParser(usage=usage_example)
    optparser.add_option("--output-dir", action="store", dest="output_path",
                         help="[Required] specify the output directory")
    (options, args) = optparser.parse_args()
    if options.output_path is None:
        optparser.error("You must specify --output-dir")

    f = urllib2.urlopen(parse_url)
    parser = URLLister()
    parser.feed(f.read())
    f.close()
    parser.close()

    # get most recent file per platform
    recent_builds = getRecentBuilds(parser.builds)

    writeOutput(options.output_path, "index.html", buildHTML(recent_builds))
    writeOutput(options.output_path, "index.json", buildJSON(recent_builds))
    copyFile(options.output_path, "firefox.png")
    copyFile(options.output_path, "nightly.css")
    webm_dir = os.path.join(options.output_path, "webm")
    if not os.path.exists(webm_dir):
        os.mkdir(webm_dir)
    copyFileWithName("webm.html", webm_dir, "index.html")

if __name__ == '__main__':
    main()
