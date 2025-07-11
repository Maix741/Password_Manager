
def transform_website(website_raw: str) -> str:
    """Removes 'www.' from the website if it exists, strips protocol prefixes, and removes any trailing slashes.

    Args:
        website_raw (str): The raw website URL or domain string to be transformed.

    Returns:
        str: The cleaned website domain without protocol, 'www.', or trailing slashes.
    """
    website: str = website_raw.strip().lower()
    if website.startswith("http://www."):
        website = website[12:]
    elif website.startswith("https://www."):
        website = website[13:]

    if website.startswith("www."):
        website = website[4:]

    if website.startswith("http://"):
        website = website[7:]
    elif website.startswith("https://"):
        website = website[8:]

    website = website.rstrip("/")

    return website
