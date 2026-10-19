import urllib.request
import re

url = "https://pypi.org/simple/pyside6-essentials/"
html = urllib.request.urlopen(url).read().decode("utf-8")
matches = re.findall(r'href="([^"]+pyside6_essentials-6\.12\.0-cp310-abi3-win_amd64\.whl[^"]*)"', html)
if matches:
    print("ESSENTIALS_URL:", matches[0])

url_shiboken = "https://pypi.org/simple/shiboken6/"
html_s = urllib.request.urlopen(url_shiboken).read().decode("utf-8")
matches_s = re.findall(r'href="([^"]+shiboken6-6\.12\.0-cp310-abi3-win_amd64\.whl[^"]*)"', html_s)
if matches_s:
    print("SHIBOKEN_URL:", matches_s[0])
