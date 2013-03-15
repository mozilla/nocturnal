# Nocturnal #

Nocturnal is a simple Python scraper script that crawls Mozilla's Nightly
FTP folders to build [nightly.mozilla.org](http://nightly.mozilla.org).
This repo contains all the resources to build all Nightly pages.

You'll need to run the scraper script from a machine with an Internet
connection.

## Setup ##

Make sure you grab all the submodules.

    git clone --recursive https://github.com/mozilla/nocturnal.git

## Usage ##

Specify an output directory (it shouldn't be the same directory as the
repo) and allow a few seconds for the script to scrape Mozilla's FTP
server.

    ./scrape.py --output-dir html

License
-------
This software is licensed under the [Mozilla Tri-License][MPL]:

    ***** BEGIN LICENSE BLOCK *****
    Version: MPL 1.1/GPL 2.0/LGPL 2.1

    The contents of this file are subject to the Mozilla Public License Version
    1.1 (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at
    http://www.mozilla.org/MPL/

    Software distributed under the License is distributed on an "AS IS" basis,
    WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
    for the specific language governing rights and limitations under the
    License.

    The Original Code is Nocturnal.

    The Initial Developer of the Original Code is Mozilla.
    Portions created by the Initial Developer are Copyright (C) 2009
    the Initial Developer. All Rights Reserved.

    Contributor(s):
      Rob Sayre <sayrer@gmail.com>
      Gavin Sharp
      Matthew Riley MacPherson <tofumatt@mozilla.com>

    Alternatively, the contents of this file may be used under the terms of
    either the GNU General Public License Version 2 or later (the "GPL"), or
    the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
    in which case the provisions of the GPL or the LGPL are applicable instead
    of those above. If you wish to allow use of your version of this file only
    under the terms of either the GPL or the LGPL, and not to allow others to
    use your version of this file under the terms of the MPL, indicate your
    decision by deleting the provisions above and replace them with the notice
    and other provisions required by the GPL or the LGPL. If you do not delete
    the provisions above, a recipient may use your version of this file under
    the terms of any one of the MPL, the GPL or the LGPL.

    ***** END LICENSE BLOCK *****

[MPL]: http://www.mozilla.org/MPL/
