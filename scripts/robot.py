from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

USER_AGENT = "*"

def can_scrape(url):
    parsed = urlparse(url)

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    return rp.can_fetch(USER_AGENT, url)