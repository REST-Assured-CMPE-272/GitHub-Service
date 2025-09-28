def forward_pagination_headers(src_headers, response):
    link = src_headers.get("link")
    if link:
        response.headers["Link"] = link
