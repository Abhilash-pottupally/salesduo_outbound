from __future__ import annotations

from .discovery import SearchResult
from .providers import StaticProvider
from .run import resolve_brand


# This demonstrates the complete pipeline without requiring Serper.
# Replace this static provider with SerperProvider when an API key is available.
DEMO_RESULTS = {
    '"Chefman" official website': [SearchResult("Chefman | Kitchen Appliances", "https://chefman.com/", "Official Chefman kitchen appliances")],
    '"Chefman" Amazon brand website': [SearchResult("Chefman Amazon", "https://www.amazon.com/stores/Chefman", "Chefman brand")],
    '"Chefman" company website': [SearchResult("Chefman", "https://chefman.com/", "Kitchen products")],
}


if __name__ == "__main__":
    result = resolve_brand("Chefman", StaticProvider(DEMO_RESULTS))
    print(result)
