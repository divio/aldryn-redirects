from six.moves.urllib.parse import urlparse, parse_qsl, urlencode


def get_query_params_dict(url):
    # request.GET sounds tempting below but wouldn't work for malformed querystrings (such as '/path?hamster').
    return dict(parse_qsl(urlparse(url).query, keep_blank_values=True))


def remove_query_params(url):
    return urlparse(url)._replace(query='').geturl()


def add_query_params_to_url(url, params):
    return urlparse(url)._replace(query=urlencode(params)).geturl()
