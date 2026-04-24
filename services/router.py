from __future__ import annotations

import json
import logging
import re
import time
from typing import Optional

import anthropic
import google.generativeai as genai
import openai

import config

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Role: Senior Technical Recruiter & AI Infrastructure Expert. "
    "Evaluate the candidate resume against the job description objectively and technically. "
    "Use a scoring scale of 1 (no match) to 10 (perfect match). "
    "Total reasoning must not exceed 2 sentences. "
    "Respond strictly in the requested format."
)

_USER_TEMPLATE = (
    "[RESUME CONTEXT]\n{resume_json}\n"
    "[JOB DESCRIPTION]\n{job_desc}\n"
    "[TASK]\n"
    "Score: [X]/10\n"
    "Reasoning: Pros: [list strengths]. Cons: [list gaps]."
)


class LLMRouter:
    def evaluate(self, resume: dict, job_desc: str) -> Optional[dict]:
        resume_json = json.dumps(resume, indent=2)
        user_content = _USER_TEMPLATE.format(resume_json=resume_json, job_desc=job_desc)

        providers = [
            ("gemini-1.5-flash", lambda: self._call_gemini(user_content)),
            ("gpt-4o-mini", lambda: self._call_openai(user_content)),
            ("claude-3-haiku-20240307", lambda: self._call_claude(user_content)),
        ]

        for model_name, call_fn in providers:
            response_text = self._try_with_retry(call_fn, model_name)
            if response_text is not None:
                parsed = self._parse_response(response_text, model_name)
                if parsed is not None:
                    return parsed

        logger.critical("All LLM providers failed for job evaluation")
        return None

    def _try_with_retry(self, call_fn, model_name: str) -> Optional[str]:
        for attempt in range(2):
            try:
                return call_fn()
            except Exception as exc:
                if self._is_rate_limited(exc) and attempt == 0:
                    logger.warning(
                        "%s attempt 1 failed (%s), retrying after 2s",
                        model_name,
                        type(exc).__name__,
                    )
                    time.sleep(2)
                    continue
                logger.warning(
                    "%s failed after %d attempt(s): %s",
                    model_name,
                    attempt + 1,
                    exc,
                )
                return None
        return None  # unreachable; satisfies type checker

    def _is_rate_limited(self, exc: Exception) -> bool:
        # 429 only: retry once after 2s.  500 switches provider immediately (TS-C03).
        try:
            from google.api_core.exceptions import ResourceExhausted
            if isinstance(exc, ResourceExhausted):
                return True
        except ImportError:
            pass
        return isinstance(exc, (openai.RateLimitError, anthropic.RateLimitError))

    def _call_gemini(self, user_content: str) -> str:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=_SYSTEM_PROMPT,
        )
        response = model.generate_content(user_content)
        return response.text

    def _call_openai(self, user_content: str) -> str:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content

    def _call_claude(self, user_content: str) -> str:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        return response.content[0].text

    def _parse_response(self, text: str, model_name: str) -> Optional[dict]:
        score_match = re.search(r"Score:\s*(\d+)\s*/\s*10", text, re.IGNORECASE)
        if not score_match:
            logger.warning("Could not parse score from %s response", model_name)
            return None
        reasoning_match = re.search(r"Reasoning:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else text.strip()
        return {
            "match_score": int(score_match.group(1)),
            "reasoning": reasoning,
            "model_used": model_name,
        }
