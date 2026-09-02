from first_aid_rag.prompts.locales.en import SYSTEM_PROMPT  # shared rules
from first_aid_rag.prompts.locales.en import (
    REFUSAL_API_ERROR,
    REFUSAL_NO_RESPONSE,
    REFUSAL_GENERAL_ERROR,
    REFUSAL_MISSING_API_KEY,
)

REFUSAL_INSUFFICIENT_EVIDENCE = (
    "عذراً، المعلومات الطبية المتوفرة في المنظومة غير كافية لتقديم إجابة موثوقة."
)

REFUSAL_OUT_OF_SCOPE = (
    "عذراً، هذا السؤال خارج تخصصي. أنا مبرمج فقط لتقديم إرشادات الإسعافات الأولية لحالات الطوارئ الطبية."
)

REFUSAL_API_ERROR = "خطأ من واجهة الموديل: {error}"
REFUSAL_NO_RESPONSE = "لم يتم التوصل لاستجابة من الموديل الذكي."
REFUSAL_GENERAL_ERROR = "حدث خطأ أثناء التواصل مع الموديل: {error}"
REFUSAL_MISSING_API_KEY = "مفتاح API غير متاح في الإعدادات (.env). يرجى تعيين المفتاح."

