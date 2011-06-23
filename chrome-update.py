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
        for n, N in results:
            if n < N:
                return False
        return True

    def good_revisions(self):
        for rev, results in self.data:
            if self.is_good_enough(results):
                yield rev


class BuildData:

    def __init__(self, page):
        self.builds = self._parse_builds(page)
    
    def _parse_builds(self, page):
        result = []
        for line in page.split("\n"):
            m = re.search("href=\"([0-9]+)/\"", line)
            if m:
                result.append(m.group(1))
        return result

    def is_available(self, rev):
        return rev in self.builds

    def download(self, rev):
        src = "http://build.chromium.org/f/chromium/snapshots/Win/%s/chrome-win32.zip" % rev
        dest = "chrome-win32-%s.zip" % rev
        os.system("wget -c -O \"%s\" \"%s\"" % (dest, src))


if __name__ == '__main__':
    print "Downloading tests page..."
    page = urllib2.urlopen("http://build.chromium.org/p/chromium/console").read()
    #page = open("console").read()
    td = TestData(page)

    print "Downloading builds page..."
    page2 = urllib2.urlopen("http://build.chromium.org/f/chromium/snapshots/Win/?C=M;O=D").read()
    #page2 = open("index.html@C=M;O=D").read()
    bd = BuildData(page2)

    print

    td.print_summary()

    for rev in td.good_revisions():
        if bd.is_available(rev):
            print "found", rev
            print
            bd.download(rev)
            break
        print "not found", rev
