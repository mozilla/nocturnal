#!/usr/bin/python

from optparse import OptionParser
import os
from sgmllib import SGMLParser
import shutil
import simplejson as json
import urllib2


path_to_this_script = os.path.realpath(__file__)

usage_example = "%prog --output-dir=/tmp/path/example"

# mod_autoindex generated HTML containing builds:
apache_query_string = "?C=M;O=D"

PAGES = [
    # Desktop Site
    {
        'base_url': 'http://ftp.mozilla.org/pub/mozilla.org/',
        'builds': [
            {
                'css_class': 'windows exe',
                'extension': "exe",
                # Optional header will display above this build.
                # Sorta hacky, but hey: it works.
                'header': 'Desktop',
                'name': 'Windows',
                'suffix': '.win32.installer',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'css_class': 'windows x64 exe',
                'extension': "exe",
                'name': 'Windows 64-bit',
                'suffix': '.win64-x86_64.installer',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'css_class': 'mac dmg',
                'extension': "dmg",
                'name': 'Mac',
                'suffix': '.mac',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'css_class': 'linux bz2',
                'extension': "tar.bz2",
                'name': 'Linux Intel',
                'suffix': '.linux-i686',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'css_class': 'linux bz2 x64',
                'extension': "tar.bz2",
                'name': 'Linux 64-bit Intel',
                'suffix': '.linux-x86_64',
                'url': 'firefox/nightly/latest-trunk/',
            },
        ],
        'file': 'index',
        'more_url': 'http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/',
        'other_build_header': 'Mobile',
        'show_in_list': True,
        'title': 'Firefox Nightly Builds',
    },
    # Mobile Site
    {
        'base_url': 'http://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/',
        'builds': [
            {
                'css_class': 'android',
                'extension': "apk",
                'header': "Mobile (for Devices)",
                'name': 'Android',
                'suffix': '.multi.android-arm',
                'url': 'latest-mozilla-central-android/',
            },
            {
                'css_class': 'maemo maemo-gtk',
                'extension': "tar.bz2",
                'name': 'Maemo GTK',
                'suffix': '.multi.linux-gnueabi-arm',
                'url': 'latest-mozilla-central-maemo5-gtk/',
            },
            {
                'css_class': 'maemo maemo-qt',
                'extension': "tar.bz2",
                'name': 'Maemo QT',
                'suffix': '.multi.linux-gnueabi-arm',
                'url': 'latest-mozilla-central-maemo5-qt/',
            },
            {
                'css_class': 'windows zip',
                'extension': "zip",
                'header': 'Mobile (for Desktop OSes)',
                'name': 'Windows',
                'suffix': '.win32',
                'url': 'latest-mozilla-central-win32/',
            },
            {
                'css_class': 'mac dmg',
                'extension': "dmg",
                'name': 'Mac',
                'suffix': '.mac',
                'url': 'latest-mozilla-central-macosx/',
            },
            {
                'css_class': 'linux bz2',
                'extension': "tar.bz2",
                'name': 'Linux Intel',
                'suffix': '.linux-i686',
                'url': 'latest-mozilla-central-linux/',
            },
        ],
        'file': 'mobile',
        'more_url': 'http://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/',
        'other_build_header': 'Desktop',
        'show_in_list': True,
        'title': 'Mobile Nightly Builds',
    },
    # JS Previews
    {
        'base_url': 'http://ftp.mozilla.org/pub/mozilla.org/',
        'builds': [
            {
                'css_class': 'windows exe',
                'extension': "exe",
                'name': 'Windows',
                'suffix': '.win32.installer',
                'url': 'firefox/nightly/latest-tracemonkey/',
            },
            {
                'css_class': 'windows x64 exe',
                'extension': "exe",
                'name': 'Windows 64-bit',
                'suffix': '.win64-x86_64.installer',
                'url': 'firefox/nightly/latest-tracemonkey/',
            },
            {
                'css_class': 'mac dmg',
                'extension': "dmg",
                'name': 'Mac',
                'suffix': '.mac',
                'url': 'firefox/nightly/latest-tracemonkey/',
            },
            {
                'css_class': 'linux bz2',
                'extension': "tar.bz2",
                'name': 'Linux Intel',
                'suffix': '.linux-i686',
                'url': 'firefox/nightly/latest-tracemonkey/',
            },
            {
                'css_class': 'linux bz2 x64',
                'extension': "tar.bz2",
                'name': 'Linux 64-bit Intel',
                'suffix': '.linux-x86_64',
                'url': 'firefox/nightly/latest-tracemonkey/',
            },
        ],
        'file': 'js-preview',
        'more_url': 'http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-tracemonkey',
        'show_in_list': False,
        'title': 'Firefox JS Preview Builds',
    },
]

class URLLister(SGMLParser):
    """
    Extend SGML Parser to look through FTP listing pages on ftp.mozilla.org
    and get relevant file URLs, datestamps, and sizes.
    """
    
    def __init__(self, parse_url, name, build):
        SGMLParser.__init__(self)
        self.build = build
        self.date = None
        self.link = None
        self.parse_url = parse_url
        self.name = name
        self.size = None

    def reset(self):
        SGMLParser.reset(self)
        self.textData = ""

    def start_td(self, attrs):
        self.textData = ""

    def end_td(self):
        text = self.textData.strip()

        if (self.textData.endswith(
            '%s.%s' % (self.build['suffix'], self.build['extension']))):
            self.link = self.parse_url + text
            return

        if (self.link):
            if self.date == None:
                self.date = text.split()[0]
            elif self.size == None:
                self.size = text

    def handle_data(self, text):
        self.textData += text

def buildJSON(builds):
    """
    Take a list of builds and output JSON base on each build's dictionary
    structure.
    """
    output = []

    for build in builds:
        # Skip any builds that don't have a full link
        if build['link'] is None:
            continue
        
        # We make a copy so only certain keys show up, and we use URL over
        # link for historical reasons.
        json_build = build.copy()
        json_build['url'] = json_build['link']
        try:
            del json_build['header']
        except KeyError:
            pass
        del json_build['link']
        
        output.append(json_build)

    return json.dumps(output, indent=0)

def buildHTML(page, other_pages=None):
    """
    Build and return an HTML string with all builds supplied, a "get more"
    builds link, and the title of the page.
    
    Also takes an optional "other_pages" argument to link to other build
    pages.
    """

    try:
        other_build_header = '<h3 id="other-builds">%s</h3>' % (
                                                page['other_build_header'])
    except KeyError:
        other_build_header = ""

    header = """
<!DOCTYPE html>
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
          <ul>\n""" % page['title']

    footer_start = """
          </ul>

          %s
          <ul id="more-urls">""" % other_build_header

    footer_end = """</ul>

          <p id="ftp">We have <a href="%s">more stuff</a> if you don't see what you're looking for.</p>
        </div>
      </body>
</html>""" % page['more_url']

    builds = page['builds']
    extension = ""
    middle = ""
    more_urls = ""

    for build in builds:
        if build['link'] == None:
            continue

        # If a header key is present, add a separator element.
        try:
            middle += '<li class="header"><h3>%s</h3></li>' % build['header']
        except KeyError:
            pass

        middle += '\n<li class="' + build['css_class'] + '"'
        if build['extension'] != extension:
            middle += ' style="clear: both;"'
            extension = build['extension']
        middle += '>\n'
        middle += '<a href="' + build['link'] + '">'
        middle += build['name']
        middle += '</a>'
        middle += '' + build['size'] + 'B'
        middle += '  ' + build['extension']
        middle += '<br>\n'
        middle += '<small>Built on ' + build['date'] + '</small>\n'
        middle += '</li>'

    for p in other_pages:
        # Don't link to this page.
        if p['file'] is not page['file'] and p['show_in_list']:
            more_urls += '<li><a href="%s">%s</a></li>' % (
                                            p['file'] + '.html', p['title'])

    return header + middle + footer_start + more_urls + footer_end

def copy_file(output_dir, fileName):
    """Helper function that copies a file to a new folder."""
    resource_path = os.path.split(path_to_this_script)[0]
    shutil.copyfile(os.path.join(resource_path, fileName),
                    os.path.join(output_dir, fileName))

def generate_build_files(page, output_path):
    """Generate an HTML file and JSON file using the page info provided."""
    for build in page['builds']:
        f = urllib2.urlopen(
            page['base_url'] + build['url'] + apache_query_string)
        parser = URLLister(page['base_url'] + build['url'], build['name'],
                            build)
        parser.feed(f.read())
        f.close()
        parser.close()

        build['date'] = parser.date
        build['link'] = parser.link
        build['size'] = parser.size

    # Create the HTML page for this page.
    write_output(output_path, '%s.html' % page['file'],
                    buildHTML(page, PAGES))
    # Create the JSON file afterward.
    write_output(output_path, '%s.json' % page['file'],
                    buildJSON(page['builds']))

def write_output(output_dir, filename, text):
    """Helper function that writes a string out to a file."""
    f = open(os.path.join(output_dir, filename), 'w')
    f.write(text)
    f.close()

def main():
    """
    Function run when script is run from the command line. Generates new pages
    based on the PAGES variable.
    """
    optparser = OptionParser(usage=usage_example)
    optparser.add_option("--output-dir", action="store", dest="output_path",
                         help="[Required] specify the output directory")
    (options, args) = optparser.parse_args()
    if options.output_path is None:
        optparser.error("You must specify --output-dir")

    for page in PAGES:
        generate_build_files(page, options.output_path)

    copy_file(options.output_path, "android.png")
    copy_file(options.output_path, "blueGradient.png")
    copy_file(options.output_path, "maemo.png")
    copy_file(options.output_path, "nightly.css")
    copy_file(options.output_path, "nightly.png")

if __name__ == '__main__':
    main()
