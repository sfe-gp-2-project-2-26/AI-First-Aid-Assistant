from first_aid_rag.utils.clinical_regex import (
    is_page_number_text,
    is_boilerplate_text,
    extract_nice_recommendation_id,
    extract_esc_metadata
)

def test_is_page_number_text_simple():
    assert is_page_number_text("5") is True
    assert is_page_number_text("  5  ") is True

def test_is_page_number_text_compound():
    assert is_page_number_text("Page 5 of 20") is True
    assert is_page_number_text("Page 5/20") is True

def test_is_page_number_text_not_page():
    assert is_page_number_text("Hello World") is False
    assert is_page_number_text("CPR Steps") is False

def test_is_boilerplate_copyright():
    assert is_boilerplate_text("© 2024 All rights reserved") is True
    assert is_boilerplate_text("Copyright 2025") is True

def test_is_boilerplate_downloaded():
    assert is_boilerplate_text("Downloaded from medical site") is True

def test_is_boilerplate_normal_text():
    assert is_boilerplate_text("Apply pressure to the wound") is False

def test_extract_nice_recommendation_id():
    assert extract_nice_recommendation_id("Recommendation 1.2.3") == "1.2.3"
    assert extract_nice_recommendation_id("NICE Rec 4.5") == "4.5"
    assert extract_nice_recommendation_id("No numbers here") is None

def test_extract_esc_metadata_class_level():
    cls, lvl = extract_esc_metadata("Class IIa Level B")
    assert cls == "IIA"
    assert lvl == "B"
    
    cls2, lvl2 = extract_esc_metadata("Some text Class I and Level C")
    assert cls2 == "I"
    assert lvl2 == "C"

