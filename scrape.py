#!/usr/bin/python

usage_example = "%prog --output-dir=/tmp/path/example"

# mod_autoindex generated HTML containing builds:
apache_query_string = "?C=M;O=D"
build_pages = [
    {"url":"http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/",
     "title": "Firefox Nightly Builds",
     "html": "index.html"},
    {"url":"http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-tracemonkey/",
     "title": "Firefox JS Preview Builds",
     "html": "js-preview.html"}
]

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
    BuildDisplay(".linux-i686",             "tar.bz2", "Linux Intel",         "linux bz2"),
    BuildDisplay(".linux-x86_64",           "tar.bz2", "Linux 64-bit Intel",  "linux bz2 x64")
]

wanted_keys = tuple([f.suffix + "." + f.extension for f in files_wanted])

def build(url, files_wanted):
    d = {}
    d['url'] = url
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
    def __init__(self, parse_url):
        SGMLParser.__init__(self)
        self.parse_url = parse_url

    def reset(self):
        SGMLParser.reset(self)
        self.builds = []
        self.textData = ""
            
    def start_td(self, attrs):
        self.textData = ""

    def end_td(self):
        text = self.textData.strip()

        if (self.textData.endswith(wanted_keys)):
            self.builds.append(build(self.parse_url + text, files_wanted))
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

def buildHTML(recent_builds, parse_url, title):
    header = """<!DOCTYPE html>
<html>
      <head>
        <title>Firefox Nightly Builds</title>
        <link rel="stylesheet" type="text/css" href="http://www.mozilla.com/style/tignish/content.css" />
        <link rel="stylesheet" type="text/css" href="nightly.css" />
      </head>
      <body>
        <div id="main-feature">
          <h1>%s</h1>
          <p>These builds are for testing purposes only.</p>
        </div>
        <div id="builds">
          <ul>\n""" % title
    
    footer = """
          </ul>
                
          <p>We have <a href="%s">more stuff</a> if you don't see what you're looking for.</p>
        </div>
      </body>
</html>""" % parse_url
    
    extension = ""
    middle = ""
    for build in recent_builds:
        middle += '\n<li class="' + build['css_class'] + '"'
        if build['extension'] != extension:
            middle += 'style="clear: both;"'
            extension = build['extension']
        middle += '>\n'
        middle += '<a href="' + build['url'] + '">'
        middle += build['name']
        middle += '</a>'
        middle += '' + build['size'] + 'B'
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
    items = []        
    for f in files_wanted:
        if recent_builds_dict.has_key(f.css_class):
            items.append((f.css_class, recent_builds_dict[f.css_class]))
    
    return [value for key, value in items]

def generateBuildPages(output_path, parse_url, dest_page, title):
    f = urllib2.urlopen(parse_url + apache_query_string)
    parser = URLLister(parse_url)
    parser.feed(f.read())
    f.close()
    parser.close()

    # get most recent file per platform
    recent_builds = getRecentBuilds(parser.builds)

    writeOutput(output_path, dest_page, buildHTML(recent_builds, parse_url, title))
    writeOutput(output_path, dest_page[:dest_page.find(".html")] + ".json", buildJSON(recent_builds))

def main():
    optparser = OptionParser(usage=usage_example)
    optparser.add_option("--output-dir", action="store", dest="output_path",
                         help="[Required] specify the output directory")
    (options, args) = optparser.parse_args()
    if options.output_path is None:
        optparser.error("You must specify --output-dir")

    for page in build_pages:
        generateBuildPages(options.output_path, page["url"], page["html"], page["title"])

    copyFile(options.output_path, "nightly.png")
    copyFile(options.output_path, "blueGradient.png")
    copyFile(options.output_path, "nightly.css")

if __name__ == '__main__':
    main()
