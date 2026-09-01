import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx


def canonical_domain(value: str) -> str:
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    host = urlparse(value).netloc.lower().split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def validate_site(domain: str, brand: str, timeout: float = 10.0) -> dict:
    """Fetch a candidate homepage and collect simple identity evidence.

    This is intentionally evidence collection, not an automatic acceptance decision.
    Search/provider integrations will be added separately.
    """
    domain = canonical_domain(domain)
    url = f"https://{domain}/"
    result = {"domain": domain, "url": url, "reachable": False, "title": "", "text": ""}
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": "SalesDuoDomainResolver/0.1"}) as client:
            response = client.get(url)
            response.raise_for_status()
            result["reachable"] = True
            final_domain = canonical_domain(str(response.url))
            result["final_domain"] = final_domain
            soup = BeautifulSoup(response.text, "html.parser")
            result["title"] = soup.title.get_text(" ", strip=True) if soup.title else ""
            result["text"] = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))[:5000]
    except Exception as exc:
        result["error"] = str(exc)
    return result
