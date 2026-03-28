from first import get_market_avg

def test_scraper():
    print("Testing scraper for Lagos, Ajah, houses, 3 bedrooms...")
    avg = get_market_avg("Lagos", "Ajah", "houses", 3)
    if avg:
        print(f"SUCCESS: Market average found: N{avg:,.0f}")
    else:
        print("FAILURE: Could not find market average.")

if __name__ == "__main__":
    test_scraper()
