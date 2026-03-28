from first import verify_listing

def test_verification():
    sample_text = "3 bedroom house in Barnawa Kaduna for 25m"
    print(f"Testing verification with: '{sample_text}'")
    report = verify_listing(sample_text)
    print("\n--- REPORT ---")
    print(report)

if __name__ == "__main__":
    test_verification()
