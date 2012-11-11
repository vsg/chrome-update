# -*- coding: utf-8 -*-
#
# Purpose:
#    Download latest stable (passes all tests) development build of Chrome for Windows.
#
# Requirements: 
#    Python
#    Wget for Windows (http://users.ugent.be/~bpuype/wget/)
#

import urllib2
import re, os


class TestData:

    def __init__(self, test_page):
        self.test_data = self._parse_test_data(test_page)

    def _parse_test_data(self, test_page):
        test_data = []
        for snip in re.split("class='DevRev", test_page):
            m = re.search(r"<a .*?>([0-9]+)</a>", snip)
            if m:
                revision = m.group(1)
                num_ok = len(re.findall(r"class='DevStatusBox success", snip))
                num_total = len(re.findall(r"<td class='DevStatusBox'>", snip))
                test_data.append((revision, (num_ok, num_total)))
        return test_data

    def print_summary(self):
        for revision, (num_ok, num_total) in self.test_data:
            print revision, "%2d / %-3d" % (num_ok, num_total), "+" if num_ok == num_total else ""

    def good_revisions(self):
        for revision, (num_ok, num_total) in self.test_data:
            if num_ok == num_total:
                yield revision


def is_available(revision):
    try:
        urllib2.urlopen("http://commondatastorage.googleapis.com/chromium-browser-snapshots/Win/%s/chrome-win32.zip" % revision)
        return True
    except:
        return False

def download(revision):
    src = "http://commondatastorage.googleapis.com/chromium-browser-snapshots/Win/%s/chrome-win32.zip" % revision
    dest = "chrome-win32-%s.zip" % revision
    os.system("wget -c -O \"%s\" \"%s\"" % (dest, src))


if __name__ == '__main__':
    print "Downloading tests page..."
    print

    page = urllib2.urlopen("http://build.chromium.org/p/chromium.win/console").read()
    #page = open("console").read()

    td = TestData(page)
    
    td.print_summary()

    for revision in td.good_revisions():
        if is_available(revision):
            print "found", revision
            print
            download(revision)
            break
        print "not found", revision
