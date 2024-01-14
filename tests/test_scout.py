import sys, os

try: 
    from mailscout import Scout
except:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from mailscout import Scout


# Sample data for testing
TEST_DOMAIN = "example.com"
TEST_NAMES = ["batuhan", "akyazi"]
TEST_EMAIL = "test@example.com"

scout = Scout()

def test_check_smtp():
    # Just a test for output format
    assert scout.check_smtp(TEST_EMAIL) in [True, False]


def test_check_email_catchall():
    # This test depends on whether TEST_DOMAIN is a catch-all domain
    assert scout.check_email_catchall(TEST_DOMAIN) in [True, False]

def test_generate_prefixes():
    # Test with default prefixes
    default_prefixes = scout.generate_prefixes(TEST_DOMAIN)
    assert isinstance(default_prefixes, list) and len(default_prefixes) > 0
    # Test with custom prefixes
    custom_prefixes = scout.generate_prefixes(TEST_DOMAIN, ["custom1", "custom2"])
    assert custom_prefixes == ["custom1@example.com", "custom2@example.com"]

def test_generate_email_variants():
    variants = scout.generate_email_variants(TEST_NAMES, TEST_DOMAIN)
    assert isinstance(variants, list) and len(variants) > 0

def test_find_valid_emails():
    # Basic test to check function execution
    valid_emails = scout.find_valid_emails(TEST_DOMAIN, TEST_NAMES)
    assert isinstance(valid_emails, list)

def test_find_valid_emails_bulk():
    email_data = [{"domain": TEST_DOMAIN, "names": TEST_NAMES}]
    bulk_result = scout.find_valid_emails_bulk(email_data)
    assert isinstance(bulk_result, list) and len(bulk_result) > 0

def test_normalize_name_basic():
    assert scout.normalize_name("John") == "john"
    assert scout.normalize_name("ANNA") == "anna"
    assert scout.normalize_name("Akyazı") == "akyazi"
    assert scout.normalize_name("Şahin") == "sahin"
    assert scout.normalize_name("François") == "francois"
    assert scout.normalize_name("Łćłąńśşöü") == "lclanssou"