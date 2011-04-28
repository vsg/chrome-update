# -*- coding: utf-8 -*-
#
# Purpose:
#    Download latest stable (passes all tests) development build of Chrome for Windows.
#
# Requirements:
#    Python (http://www.python.org/getit/)
#    Wget for Windows (http://users.ugent.be/~bpuype/wget/)
#

import urllib2
import re, os

def find_rev(page):
    revs = []
    for div in re.split("class='DevRev", page):
        m = re.search(r"<a .*?>([0-9]+)</a>", div)
        if m:
            rev = m.group(1)
            lines = filter(lambda line: "addBox(\"" in line, div.split("\n"))
            ok = filter(lambda line: "\"success\"" in line, lines)
            print "%s  %2i/%i  %s" % (rev, len(ok), len(lines), "+" if len(lines) == len(ok) else "")
            if len(lines) == len(ok):
                revs.append(rev)
    return revs


def find_build(page, rev):
    for line in page.split("\n"):
        m = re.search("href=\"([0-9]+)/\"", line)
        if m:
            if m.group(1) == rev:
                cmd = "wget -O chrome-win32-%s.zip http://build.chromium.org/f/chromium/snapshots/chromium-rel-xp/%s/chrome-win32.zip"
                os.system(cmd % (rev, rev))
                return True


print "Downloading tree page..."
page = urllib2.urlopen("http://build.chromium.org/p/chromium/console").read()

print "Downloading builds page..."
page2 = urllib2.urlopen("http://build.chromium.org/buildbot/snapshots/chromium-rel-xp/?C=M;O=D").read()

for rev in find_rev(page):
    if find_build(page2, rev):
        print "found " + rev
        break
    else:
        print "not found " + rev
