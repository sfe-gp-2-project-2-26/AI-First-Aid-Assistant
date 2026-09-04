import json
import logging
from typing import List, Optional
import httpx

from first_aid_rag.interfaces.llm_interface import LLMProvider
from first_aid_rag.schemas.llm import ClinicalLLMResponse, Citation
from first_aid_rag.schemas.query_processing import ProcessedQuery
from first_aid_rag.models.enums.first_aid_topics import FirstAidTopic
from first_aid_rag.config import settings
from first_aid_rag.prompts.manager import PromptManager, detect_locale

logger = logging.getLogger(__name__)



class GeminiLLMProvider(LLMProvider):
    """Google Gemini API Provider for Clinical LLM Generation with Citation Tracking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.timeout = timeout
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    def _format_context(self, docs: List[dict]) -> str:
        if not docs:
            return "No clinical context available."

        formatted_chunks = []
        for idx, doc in enumerate(docs, 1):
            chunk_id = doc.get("chunk_id", f"chunk_{idx}")
            text = doc.get("text", "")
            pdf_page = doc.get("pdf_page", 1)
            section = doc.get("section", "")
            rec_id = doc.get("recommendation_id") or "N/A"
            rec_class = doc.get("recommendation_class") or "N/A"
            evidence_lvl = doc.get("evidence_level") or "N/A"
            score = doc.get("percentage_score", 0.0)

            source = doc.get("source", "")
            chunk_str = (
                f"--- CHUNK HEADER ---\n"
                f"chunk_id: {chunk_id}\n"
                f"source_file: {source}\n"
                f"recommendation_id: {rec_id}\n"
                f"recommendation_class: {rec_class}\n"
                f"evidence_level: {evidence_lvl}\n"
                f"pdf_page: {pdf_page}\n"
                f"section: {section}\n"
                f"confidence_score: {score}%\n"
                f"--- TEXT CONTENT ---\n{text}\n"
            )
            formatted_chunks.append(chunk_str)

        return "\n\n".join(formatted_chunks)

    async def generate(
        self,
        query: str,
        filtered_docs: List[dict],
        system_prompt: Optional[str] = None,
    ) -> ClinicalLLMResponse:
        """Generate structured clinical response using Google Gemini API with Citation tracking."""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Returning default fallback refusal.")
            locale = detect_locale(query)
            return ClinicalLLMResponse(
                is_in_scope=True,
                is_knowledge_sufficient=False,
                answer=None,
                citations=[],
                refusal_reason=PromptManager().get_missing_api_key_refusal(locale),
                provider="gemini",
                model_name=self.model_name,
                filtered_chunks_count=len(filtered_docs),
            )

        context_text = self._format_context(filtered_docs)
        sys_instructions = system_prompt or PromptManager().get_system_prompt(detect_locale(query))

        user_content = f"CLINICAL CONTEXT CHUNKS:\n{context_text}\n\nUSER CLINICAL QUERY: {query}"

        # Define JSON Response Schema for Gemini Structured Outputs
        json_schema = {
            "type": "OBJECT",
            "properties": {
                "is_in_scope": {
                    "type": "BOOLEAN",
                    "description": "True if query is strictly about First Aid / Emergency Response. False otherwise."
                },
                "is_knowledge_sufficient": {
                    "type": "BOOLEAN",
                    "description": "True if context contains sufficient first aid clinical evidence. False otherwise."
                },
                "answer": {
                    "type": "STRING",
                    "nullable": True,
                    "description": "Concise first-aid response formatted in bullet points. Must be null if either flag is false."
                },
                "citations": {
                    "type": "ARRAY",
                    "description": "List of chunks actually used to construct the answer. Must be empty if answer is null.",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "chunk_id": {"type": "STRING"},
                            "recommendation_id": {"type": "STRING", "nullable": True},
                            "pdf_page": {"type": "INTEGER", "nullable": True},
                            "section": {"type": "STRING", "nullable": True}
                        },
                        "required": ["chunk_id"]
                    }
                },
                "refusal_reason": {
                    "type": "STRING",
                    "nullable": True,
                    "description": "Polite refusal message in user's query language if out of scope or insufficient knowledge."
                }
            },
            "required": ["is_in_scope", "is_knowledge_sufficient", "citations"]
        }

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_content}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": sys_instructions}]
            },
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": json_schema
            }
        }

        headers = {"Content-Type": "application/json"}
        url = f"{self.base_url}?key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"⚡ Sending generation request to Gemini ({self.model_name})...")
                res = await client.post(url, json=payload, headers=headers)

                if res.status_code != 200:
                    logger.error(f"Gemini API error ({res.status_code}): {res.text}")
                    locale = detect_locale(query)
                    return ClinicalLLMResponse(
                        is_in_scope=True,
                        is_knowledge_sufficient=False,
                        answer=None,
                        citations=[],
                        refusal_reason=PromptManager().get_api_error_refusal(locale, str(res.status_code)),
                        provider="gemini",
                        model_name=self.model_name,
                        filtered_chunks_count=len(filtered_docs),
                    )

                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    locale = detect_locale(query)
                    return ClinicalLLMResponse(
                        is_in_scope=True,
                        is_knowledge_sufficient=False,
                        answer=None,
                        citations=[],
                        refusal_reason=PromptManager().get_no_response_refusal(locale),
                        provider="gemini",
                        model_name=self.model_name,
                        filtered_chunks_count=len(filtered_docs),
                    )

                raw_json_str = candidates[0]["content"]["parts"][0]["text"]
                parsed_data = json.loads(raw_json_str)

                is_in_scope = bool(parsed_data.get("is_in_scope", False))
                is_knowledge_sufficient = bool(parsed_data.get("is_knowledge_sufficient", False))
                answer = parsed_data.get("answer")
                refusal_reason = parsed_data.get("refusal_reason")

                # Build lookup dict for original doc text
                docs_by_id = {str(d.get("chunk_id")): d for d in filtered_docs}

                raw_citations = parsed_data.get("citations", [])
                citations_list: List[Citation] = []
                if isinstance(raw_citations, list):
                    for c in raw_citations:
                        if isinstance(c, dict) and "chunk_id" in c:
                            cid = str(c["chunk_id"])
                            matched_doc = docs_by_id.get(cid, {})
                            matched_text = matched_doc.get("text", "")

                            citations_list.append(
                                Citation(
                                    chunk_id=cid,
                                    source=matched_doc.get("source"),
                                    document_id=matched_doc.get("document_id"),
                                    recommendation_id=c.get("recommendation_id") if c.get("recommendation_id") and str(c.get("recommendation_id")).upper() != "N/A" else matched_doc.get("recommendation_id"),
                                    pdf_page=c.get("pdf_page") or matched_doc.get("pdf_page"),
                                    section=c.get("section") if c.get("section") and str(c.get("section")).upper() != "N/A" else matched_doc.get("section"),
                                    source_text=matched_text,
                                    score=matched_doc.get("score"),
                                    percentage_score=matched_doc.get("percentage_score"),
                                )
                            )

                # Enforce AND-Gate locally as additional guardrail
                if not (is_in_scope and is_knowledge_sufficient):
                    answer = None
                    citations_list = []
                    if not refusal_reason:
                        locale = detect_locale(query)
                        if not is_in_scope:
                            refusal_reason = PromptManager().get_out_of_scope_refusal(locale)
                        else:
                            refusal_reason = PromptManager().get_insufficient_evidence_refusal(locale)

                return ClinicalLLMResponse(
                    is_in_scope=is_in_scope,
                    is_knowledge_sufficient=is_knowledge_sufficient,
                    answer=answer,
                    citations=citations_list,
                    refusal_reason=refusal_reason,
                    provider="gemini",
                    model_name=self.model_name,
                    filtered_chunks_count=len(filtered_docs),
                )

        except Exception as e:
            logger.error(f"Failed to generate response via Gemini: {e}")
            locale = detect_locale(query)
            return ClinicalLLMResponse(
                is_in_scope=True,
                is_knowledge_sufficient=False,
                answer=None,
                citations=[],
                refusal_reason=PromptManager().get_general_error_refusal(locale, str(e)),
                provider="gemini",
                model_name=self.model_name,
                filtered_chunks_count=len(filtered_docs),
            )

    async def process_query(self, query: str) -> ProcessedQuery:
        """Process the query: detect locale, check scope, translate, rewrite, and classify topic."""
        locale = detect_locale(query)
        
        if not self.api_key:
            return ProcessedQuery(
                original_query=query,
                processed_query=query,
                locale=locale,
                is_in_scope=True,
                topic_category=FirstAidTopic.GENERAL_APPROACH,
                refusal_reason=None,
            )
            
        json_schema = {
            "type": "OBJECT",
            "properties": {
                "is_in_scope": {"type": "BOOLEAN"},
                "topic_category": {
                    "type": "STRING",
                    "enum": [t.value for t in FirstAidTopic],
                },
                "processed_query": {
                    "type": "STRING",
                    "description": "English, highly optimized search query for vector retrieval.",
                },
                "refusal_reason": {"type": "STRING", "nullable": True},
            },
            "required": ["is_in_scope", "topic_category", "processed_query"],
        }
        
        payload = {
            "contents": [{"parts": [{"text": f"User Query: {query}"}]}],
            "systemInstruction": {
                "parts": [{"text": PromptManager().get_query_processing_prompt(locale)}]
            },
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json",
                "responseSchema": json_schema,
            },
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                if res.status_code == 200:
                    data = res.json()
                    raw_json_str = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_json_str)
                    
                    is_in_scope = bool(parsed.get("is_in_scope", False))
                    processed_query = parsed.get("processed_query", query)
                    topic_str = parsed.get("topic_category", FirstAidTopic.OUT_OF_SCOPE.value)
                    
                    try:
                        topic = FirstAidTopic(topic_str)
                    except ValueError:
                        topic = FirstAidTopic.OUT_OF_SCOPE

                    return ProcessedQuery(
                        original_query=query,
                        processed_query=processed_query,
                        locale=locale,
                        is_in_scope=is_in_scope,
                        topic_category=topic,
                        refusal_reason=parsed.get("refusal_reason"),
                    )
                else:
                    logger.error(f"Gemini API error during process_query: {res.text}")
                    return ProcessedQuery(
                        original_query=query,
                        processed_query=query,
                        locale=locale,
                        is_in_scope=True,
                        topic_category=FirstAidTopic.GENERAL_APPROACH,
                        refusal_reason=None,
                    )
        except Exception as e:
            logger.error(f"Failed to process query via Gemini: {e}")
            return ProcessedQuery(
                original_query=query,
                processed_query=query,
                locale=locale,
                is_in_scope=True,
                topic_category=FirstAidTopic.GENERAL_APPROACH,
                refusal_reason=None,
            )

    async def check_health(self) -> bool:
        """Check if Gemini API Key is configured and service endpoint is reachable."""
        return bool(self.api_key)
