from first_aid_rag.prompts.manager import PromptManager, detect_locale

def test_detect_locale_arabic():
    assert detect_locale("كيفية الإنعاش القلبي") == "ar"

def test_detect_locale_english():
    assert detect_locale("How to perform CPR") == "en"

def test_detect_locale_mixed():
    assert detect_locale("How to perform CPR - طريقة الإنعاش") == "ar"

def test_prompt_manager_get_system_prompt():
    pm = PromptManager()
    assert "First Aid" in pm.get_system_prompt("en")
    assert "First Aid" in pm.get_system_prompt("ar")  # shared

def test_get_out_of_scope_refusal_en():
    pm = PromptManager()
    refusal = pm.get_out_of_scope_refusal("en")
    assert "out of my scope" in refusal

def test_get_out_of_scope_refusal_ar():
    pm = PromptManager()
    refusal = pm.get_out_of_scope_refusal("ar")
    assert "خارج تخصصي" in refusal

def test_get_insufficient_evidence_refusal_en():
    pm = PromptManager()
    refusal = pm.get_insufficient_evidence_refusal("en")
    assert "insufficient" in refusal

def test_get_insufficient_evidence_refusal_ar():
    pm = PromptManager()
    refusal = pm.get_insufficient_evidence_refusal("ar")
    assert "غير كافية" in refusal

def test_get_api_error_refusal_formats_error():
    pm = PromptManager()
    refusal = pm.get_api_error_refusal("en", error="500 Server Error")
    assert "500 Server Error" in refusal

def test_get_missing_api_key_refusal():
    pm = PromptManager()
    refusal = pm.get_missing_api_key_refusal("en")
    assert "API key is missing" in refusal

def test_unknown_locale_fallback_to_en():
    pm = PromptManager()
    # "fr" is not supported, should fallback to "en"
    refusal = pm.get_out_of_scope_refusal("fr")
    assert "out of my scope" in refusal

