def format_diff(page_url, text_diff, links_diff):
    return f"""
Url Checker checkin-in!\r\n
This page has changed: {page_url}\r\n
Text Diff:\r\n
{''.join(text_diff)}\r\n
Links Diff:\r\n
{''.join(links_diff)}\r\n
"""

def format_diff_html(page_url, text_diff, links_diff):
    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Url Checker checkin-in!</title>
</head>
<body>
This page has changed: {page_url}

<p>
Text Diff: <br>
{''.join(text_diff)}
</p>

<p>
Links Diff: <br>
{''.join(links_diff)}
</p>

</body>
</html>
"""
