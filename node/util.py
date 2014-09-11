from os import system
from os import uname


def open_default_webbrowser(url):
    open_browser_cmds = {'Darwin': 'open',
                         'Linux': 'sensible-browser',
                         'Windows': 'start'}
    try:
        system("%s %s" % (open_browser_cmds[uname()[0]], url))
    except:
        print "[openbazaar:utils.open_default_webbrowser] Could not open default web browser at", url
