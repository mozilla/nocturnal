# Nocturnal #

Nocturnal is a simple Python scraper script that crawls Mozilla's Nightly
FTP folders to build [nightly.mozilla.org][nightly].
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

## Deploy ##

To deploy nocturnal to [nightly.mozilla.org][nightly], you'll need to
[file a bug in Bugzilla][bug template] under "Server Operations".

You can [use this bug template][bug template] to file a deploy bug. Easy!

You only need to get IT to deploy if you've changed the code; the
`scrape.py` command is run every hour.

[bug template]: https://bugzilla.mozilla.org/enter_bug.cgi?assigned_to=server-ops-webops%40mozilla-org.bugs&bug_file_loc=http%3A%2F%2F&bug_ignored=0&bug_severity=normal&bug_status=NEW&cf_fx_iteration=---&cf_fx_points=---&comment=Howdy%20friendly%20server%20admins%21%0D%0A%0D%0AWe%27ve%20updated%20nightly.mozilla.org%27s%20git%20repo%2C%20so%20please%20pull%20the%20latest%20version%20from%20the%20git%20repo%20and%20run%20the%20deploy%20script%20to%20update%20the%20site.%20Cheers%21&component=WebOps%3A%20Other&contenttypemethod=autodetect&contenttypeselection=text%2Fplain&flag_type-4=X&flag_type-481=X&flag_type-607=X&flag_type-674=X&flag_type-791=X&flag_type-800=X&flag_type-811=X&form_name=enter_bug&maketemplate=Remember%20values%20as%20bookmarkable%20template&op_sys=Unspecified&priority=--&product=Infrastructure%20%26%20Operations&qa_contact=smani%40mozilla.com&rep_platform=Unspecified&short_desc=Push%20new%20version%20of%20nightly.mozilla.org&target_milestone=---&version=other
[nightly]: https://nightly.mozilla.org/

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
