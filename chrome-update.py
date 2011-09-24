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


SKIP_TEST_GROUPS = ["mac", "linux", "chromiumos"]


class TestData:

    def __init__(self, page):
        self.groups = self._parse_groups(page)
        self.data = self._parse_data(page)

    def _parse_groups(self, page):
        result = []
        for line in page.split("\n"):
            m = re.search(r"<td class='DevStatus Alt .*?>(.*?)</td>", line)
            if m:
                result.append(m.group(1))
        return result

    def _parse_data(self, page):
        data = []
        for div in re.split("class='DevRev", page):
            m = re.search(r"<a .*?>([0-9]+)</a>", div)
            if m:
                rev = m.group(1)
                results = []
                for grp in re.split("class='DevStatus ", div) [1:]:
                    lines = filter(lambda line: "addBox(\"" in line, grp.split("\n"))
                    ok = filter(lambda line: "\"success\"" in line, lines)
                    results.append((len(ok), len(lines)))
                data.append((rev, results))
        return data

    def print_summary(self):
        print " " * 6,
        for name in self.groups:
            print "%-8s" % name,
        print
        for rev, results in self.data:
            print rev,
            for n, N in results:
                print "%2d / %-3d" % (n, N),
            if self.is_good_enough(results):
                print "+",
            print

    def is_good_enough(self, results):
        for name, (n, N) in zip(self.groups, results):
            if name in SKIP_TEST_GROUPS:
                continue
            if n < N:
                return False
        return True

    def good_revisions(self):
        for rev, results in self.data:
            if self.is_good_enough(results):
                yield rev


def is_available(rev):
    try:
        urllib2.urlopen("http://commondatastorage.googleapis.com/chromium-browser-snapshots/Win/%s/chrome-win32.zip" % rev)
        return True
    except:
        return False

def download(rev):
    src = "http://commondatastorage.googleapis.com/chromium-browser-snapshots/Win/%s/chrome-win32.zip" % rev
    dest = "chrome-win32-%s.zip" % rev
    os.system("wget -c -O \"%s\" \"%s\"" % (dest, src))


if __name__ == '__main__':
    print "Downloading tests page..."
    print

    page = urllib2.urlopen("http://build.chromium.org/p/chromium/console").read()
    #page = open("console").read()
    td = TestData(page)

    td.print_summary()

    for rev in td.good_revisions():
        if is_available(rev):
            print "found", rev
            print
            download(rev)
            break
        print "not found", rev
