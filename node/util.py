import webbrowser


def open_default_webbrowser(url, protocol="http"):
    """
    Open URL at the default browser.

    @param url: The URL to open.
    @type url: str

    @param protocol: The internet protocol to use.
    @type protocol: str

    @return: True on success, False on failure.
    @rtype: bool
    """
    if not url.startswith(protocol):
        # If protocol is absent from the url, attach it, otherwise
        # the file `url` will be opened in Linux flavors.
        full_url = "%s://%s" % (protocol, url)
    else:
        full_url = url

    try:
        success = webbrowser.open(full_url)
    except webbrowser.Error:
        success = False
        print "[openbazaar:%s.%s] Could not open default web browser at %s" % (
            "util",
            "open_default_webbrowser",
            url
        )
    return success
