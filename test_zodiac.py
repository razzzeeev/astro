"""Test the new zodiac algorithm"""
from datetime import date
from app.services.zodiac import get_zodiac_sign

# Test cases covering all zodiac signs and edge cases
test_cases = [
    # Format: (date, expected_sign)
    (date(1990, 1, 1), "Capricorn"),
    (date(1990, 1, 19), "Capricorn"),
    (date(1990, 1, 20), "Aquarius"),
    (date(1990, 2, 18), "Aquarius"),
    (date(1990, 2, 19), "Pisces"),
    (date(1990, 3, 20), "Pisces"),
    (date(1990, 3, 21), "Aries"),
    (date(1990, 4, 19), "Aries"),
    (date(1990, 4, 20), "Taurus"),
    (date(1990, 5, 20), "Taurus"),
    (date(1990, 5, 21), "Gemini"),
    (date(1990, 6, 20), "Gemini"),
    (date(1990, 6, 21), "Cancer"),
    (date(1990, 7, 22), "Cancer"),
    (date(1990, 7, 23), "Leo"),
    (date(1990, 8, 22), "Leo"),
    (date(1990, 8, 23), "Virgo"),
    (date(1990, 9, 22), "Virgo"),
    (date(1990, 9, 23), "Libra"),
    (date(1990, 10, 22), "Libra"),
    (date(1990, 10, 23), "Scorpio"),
    (date(1990, 11, 21), "Scorpio"),
    (date(1990, 11, 22), "Sagittarius"),
    (date(1990, 12, 21), "Sagittarius"),
    (date(1990, 12, 22), "Capricorn"),
    (date(1990, 12, 31), "Capricorn"),
    # Additional test cases
    (date(1995, 7, 23), "Leo"),
    (date(2000, 3, 21), "Aries"),
    (date(2010, 12, 22), "Capricorn"),
]

def test_zodiac():
    print("=" * 60)
    print("Testing Zodiac Algorithm")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for birth_date, expected in test_cases:
        result = get_zodiac_sign(birth_date)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            print(f"{status} {birth_date.strftime('%Y-%m-%d')} -> Expected: {expected}, Got: {result}")
    
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✓ All zodiac tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(test_zodiac())

