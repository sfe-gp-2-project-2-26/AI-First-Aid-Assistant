import pytest
from unittest.mock import patch, Mock
import httpx
import os
from first_aid_rag.stores.document_parser.providers.remote_docling import DoclingProvider

@patch("httpx.Client.post")
def test_parse_pdf_success(mock_post, tmp_path):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "total_pages": 5,
        "sections": [
            {"page_no": 1, "section_name": "Intro", "text": "Hello"}
        ],
        "tables": [
            {"page_no": 2, "caption": "Table 1", "headers": ["A"], "rows": [["1"]]}
        ],
        "figures": [
            {"page_no": 3, "caption": "Fig 1"}
        ]
    }
    mock_post.return_value = mock_resp
    
    # Create dummy pdf
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"dummy content")
    
    provider = DoclingProvider(api_url="http://test")
    doc = provider.parse_pdf(str(pdf_file), "doc_123", "Title")
    
    assert doc.document_id == "doc_123"
    assert doc.title == "Title"
    assert doc.total_pages == 5
    assert len(doc.sections) == 1
    assert doc.sections[0].text == "Hello"
    assert len(doc.tables) == 1
    assert doc.tables[0].headers == ["A"]
    assert len(doc.figures) == 1

@patch("httpx.Client.post")
def test_parse_pdf_http_error(mock_post, tmp_path):
    mock_resp = Mock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    mock_post.return_value = mock_resp
    
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"dummy content")
    
    provider = DoclingProvider(api_url="http://test")
    with pytest.raises(RuntimeError) as exc:
        provider.parse_pdf(str(pdf_file), "doc_123", "Title")
        
    assert "failed with HTTP status 500" in str(exc.value)

