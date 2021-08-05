def format_diff(page_url, text_diff, links_diff):
    return f"""
Url Checker checkin-in!\r\n
Page has changed: {page_url}\r\n
Text Diff:\r\n
{''.join(text_diff)}\r\n
Links Diff:\r\n
{''.join(links_diff)}\r\n
"""
