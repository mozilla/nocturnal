#!/usr/bin/env python

import os
import shutil
import sys
import urllib2
from optparse import OptionParser
from sgmllib import SGMLParser


# Use our local copies of simplejson and jinja2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'vendor'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'vendor', 'jinja2'))


import simplejson as json
import jinja2


# mod_autoindex generated HTML containing builds:
APACHE_QUERY_STRING = '?C=M;O=A'

CURRENT_PATH = os.path.dirname(__file__)

ENV = jinja2.Environment(loader=jinja2.FileSystemLoader([
                                os.path.join(CURRENT_PATH, 'templates'),
                                os.path.join(CURRENT_PATH, 'vendor',
                                             'django-moz-header')]),
                         extensions=['jinja2.ext.i18n'])
# We use django-moz-header, so we need to stub out the gettext functionality
# in those templates.
ENV.install_null_translations()

optparser = OptionParser(usage='%prog --output-dir=/tmp/path/example')
optparser.add_option("--output-dir", action="store", dest="output_path",
                     help="Specify the output directory")
(options, args) = optparser.parse_args()

OUTPUT_PATH = options.output_path if options.output_path else 'html'

# All the files we want to list
files = [
    # Desktop
    {
        'name': 'Desktop',
        'base_url': 'http://ftp.mozilla.org/pub/mozilla.org/',
        'builds': [
            {
                'class': 'windows',
                'extension': 'exe',
                'name': 'Windows (Express)',
                'suffix': '.win32.installer-stub',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'class': 'windows',
                'extension': 'exe',
                'name': 'Windows (Standard)',
                'suffix': '.win32.installer',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'class': 'mac',
                'extension': 'dmg',
                'name': 'Mac',
                'suffix': '.mac',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'class': 'linux',
                'extension': 'tar.bz2',
                'name': 'Linux (Intel)',
                'suffix': '.linux-i686',
                'url': 'firefox/nightly/latest-trunk/',
            },
            {
                'class': 'linux',
                'extension': 'tar.bz2',
                'name': 'Linux (Intel, 64-bit)',
                'suffix': '.linux-x86_64',
                'url': 'firefox/nightly/latest-trunk/',
            },
        ]
    },
    # Mobile (trunk)
    {
        'name': 'Mobile',
        # 'subtitle': 'For trunk (mozilla-central)',
        'base_url': 'http://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/',
        'builds': [
            {
                'class': 'android',
                'extension': 'apk',
                'name': 'Android',
                'suffix': '.multi.android-arm',
                'url': 'latest-mozilla-central-android/',
            },
            {
                'class': 'android',
                'extension': 'apk',
                'name': 'Android (ARMv6)',
                'suffix': '.multi.android-arm-armv6',
                'url': 'latest-mozilla-central-android-armv6/',
            },
            {
                'class': 'android',
                'extension': 'apk',
                'name': 'Android (x86)',
                'suffix': '.multi.android-i386',
                'url': 'latest-mozilla-central-android-x86/'

            }
        ],
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


def copy_file(output_dir, fileName):
    """Helper function that copies a file to a new folder."""
    resource_path = os.path.split(CURRENT_PATH)[0]
    shutil.copyfile(os.path.join(resource_path, fileName),
                    os.path.join(output_dir, fileName))


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
        del json_build['link']

        output.append(json_build)

    return json.dumps(output, indent=0)


def write_output(output_dir, filename, text):
    """Helper function that writes a string out to a file."""
    f = open(os.path.join(output_dir, filename), 'w')
    f.write(text)
    f.close()


def main():
    """Function run when script is run from the command line."""
    template = ENV.get_template('index.html')

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for group in files:
        for build in group['builds']:
            f = urllib2.urlopen(group['base_url'] + build['url'] +
                                APACHE_QUERY_STRING)
            parser = URLLister(group['base_url'] + build['url'], build['name'],
                               build)
            parser.feed(f.read())
            f.close()
            parser.close()

            build['date'] = parser.date
            build['link'] = parser.link
            build['size'] = parser.size

    for group in files:
        # Create the JSON file for this set of builds.
        write_output(OUTPUT_PATH, '%s.json' % group['name'].lower(),
                     buildJSON(group['builds']))

    for folder in ['css', 'fonts', 'img', 'js']:
        folder_path = os.path.join(CURRENT_PATH, OUTPUT_PATH, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        shutil.copytree(os.path.join(CURRENT_PATH, folder), folder_path)

    # Copy resources from Django-moz-header
    django_moz_header = os.path.join(CURRENT_PATH, 'vendor',
                                     'django-moz-header')
    for f in os.listdir(django_moz_header):
        if f.endswith('.css'):
            if os.path.exists(os.path.join(CURRENT_PATH, OUTPUT_PATH,
                                           'css', f)):
                os.remove(os.path.join(CURRENT_PATH, OUTPUT_PATH, 'css', f))

            shutil.copyfile(os.path.join(django_moz_header, f),
                            os.path.join(CURRENT_PATH, OUTPUT_PATH, 'css', f))
        elif f.endswith('.js'):
            if os.path.exists(os.path.join(CURRENT_PATH, OUTPUT_PATH,
                                           'js', f)):
                os.remove(os.path.join(CURRENT_PATH, OUTPUT_PATH, 'js', f))

            shutil.copyfile(os.path.join(django_moz_header, f),
                            os.path.join(CURRENT_PATH, OUTPUT_PATH, 'js', f))
        elif f.endswith('.png'):
            if os.path.exists(os.path.join(CURRENT_PATH, OUTPUT_PATH,
                                           'img', f)):
                os.remove(os.path.join(CURRENT_PATH, OUTPUT_PATH, 'img', f))

            shutil.copyfile(os.path.join(django_moz_header, f),
                            os.path.join(CURRENT_PATH, OUTPUT_PATH, 'img', f))

    write_output(OUTPUT_PATH, 'index.html', template.render({'files': files}))


if __name__ == '__main__':
    main()
