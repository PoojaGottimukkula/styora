import os
import requests
from urllib.parse import quote_plus, urlencode, urlparse, urlunparse, parse_qsl

ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")
SHORTENER_API = os.getenv("AFFILIATE_SHORTENER_API")


def _has_affiliate_params(parsed_url):
    query = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    return any(key in query for key in ("tag", "linkCode", "linkId", "ref_"))


def generate_affiliate_link(product_url):
    """
    Return a general-purpose Amazon affiliate URL.

    If the original URL already contains affiliate parameters, it is returned as-is.
    Otherwise, it appends the configured Amazon associate tag.
    """
    parsed = urlparse(product_url)
    if _has_affiliate_params(parsed) or not ASSOCIATE_TAG:
        return product_url

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["tag"] = ASSOCIATE_TAG
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _is_amazon_short_link(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")
    return host in {"amzn.to", "amzn.com"}


def shorten_link(long_url):
    """
    Shorten an affiliate URL using a configured shortener API.

    Existing Amazon short links, such as amzn.to URLs, are preserved as-is.
    The app can use them directly, but generating brand-new amzn.to links
    generally requires Amazon Associates/SiteStripe rather than a generic URL
    template.

    The environment variable AFFILIATE_SHORTENER_API should be a URL template
    containing the placeholder {url}, for example:
    https://is.gd/create.php?format=simple&url={url}

    If no shortener is configured, the original URL is returned.
    """
    if not long_url:
        return long_url

    if _is_amazon_short_link(long_url):
        return long_url

    if not SHORTENER_API:
        return long_url

    api_url = SHORTENER_API.format(url=quote_plus(long_url))
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass

    return long_url


def expand_short(short_url):
    """
    Expand a shortened URL to its full URL by following redirects.
    """
    try:
        response = requests.get(short_url, allow_redirects=True, timeout=10)
        return response.url
    except Exception:
        return short_url