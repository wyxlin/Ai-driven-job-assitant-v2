"""TSD Suite C — LLMRouter failover and retry logic."""
import logging

import pytest

from services.router import LLMRouter

_RESUME = {"name": "Lin He", "skills": {"languages": ["Python", "Java"]}}
_JOB_DESC = "Senior Backend Engineer in Seattle, WA"
_GOOD_RESPONSE = "Score: 8/10\nReasoning: Pros: strong backend. Cons: limited cloud exp."


class TestTS_C01:
    def test_normal_gemini_success(self, mocker):
        """TS-C01: Normal input → Gemini called, score + reasoning returned."""
        mock_gemini = mocker.patch.object(LLMRouter, "_call_gemini", return_value=_GOOD_RESPONSE)

        result = LLMRouter().evaluate(_RESUME, _JOB_DESC)

        assert result is not None
        assert result["match_score"] == 8
        assert result["model_used"] == "gemini-2.5-flash"
        assert "Pros:" in result["reasoning"]
        mock_gemini.assert_called_once()


class TestTS_C02:
    def test_gemini_429_retries_then_openai(self, mocker):
        """TS-C02: Gemini 429 → sleep 2s, retry once (both fail) → GPT-4o-mini succeeds."""
        from google.api_core.exceptions import ResourceExhausted

        mock_gemini = mocker.patch.object(
            LLMRouter, "_call_gemini", side_effect=ResourceExhausted("rate limited")
        )
        mock_openai = mocker.patch.object(
            LLMRouter, "_call_openai", return_value=_GOOD_RESPONSE
        )
        mock_sleep = mocker.patch("services.router.time.sleep")

        result = LLMRouter().evaluate(_RESUME, _JOB_DESC)

        assert result is not None
        assert result["model_used"] == "gpt-4o-mini"
        assert mock_gemini.call_count == 2   # attempt 0 + retry
        assert mock_openai.call_count == 1
        mock_sleep.assert_called_once_with(2)


class TestTS_C03:
    def test_openai_500_no_retry_switches_to_claude(self, mocker):
        """TS-C03: GPT-4o-mini 500 → no retry, switch immediately to Claude."""
        from google.api_core.exceptions import ResourceExhausted

        mock_gemini = mocker.patch.object(
            LLMRouter, "_call_gemini", side_effect=ResourceExhausted("rate limited")
        )
        # Non-retriable error — _is_rate_limited returns False for this
        mock_openai = mocker.patch.object(
            LLMRouter, "_call_openai", side_effect=Exception("500 internal server error")
        )
        mock_claude = mocker.patch.object(
            LLMRouter, "_call_claude", return_value=_GOOD_RESPONSE
        )
        mock_sleep = mocker.patch("services.router.time.sleep")

        result = LLMRouter().evaluate(_RESUME, _JOB_DESC)

        assert result is not None
        assert result["model_used"] == "claude-3-haiku-20240307"
        assert mock_gemini.call_count == 2   # retried (429)
        assert mock_openai.call_count == 1   # NOT retried (500 is non-retriable)
        assert mock_claude.call_count == 1
        mock_sleep.call_count == 1           # only Gemini sleep, not OpenAI


class TestTS_C04:
    def test_all_providers_fail_returns_none(self, mocker, caplog):
        """TS-C04: All providers fail → CRITICAL logged, None returned."""
        from google.api_core.exceptions import ResourceExhausted

        mocker.patch.object(LLMRouter, "_call_gemini", side_effect=ResourceExhausted("rate limited"))
        mocker.patch.object(LLMRouter, "_call_openai", side_effect=Exception("failed"))
        mocker.patch.object(LLMRouter, "_call_claude", side_effect=Exception("failed"))
        mocker.patch("services.router.time.sleep")

        with caplog.at_level(logging.CRITICAL, logger="services.router"):
            result = LLMRouter().evaluate(_RESUME, _JOB_DESC)

        assert result is None
        assert any(r.levelno == logging.CRITICAL for r in caplog.records)


class TestIsRateLimited:
    """Unit tests for _is_rate_limited exception classification."""

    def test_google_429_is_retriable(self):
        from google.api_core.exceptions import ResourceExhausted
        assert LLMRouter()._is_rate_limited(ResourceExhausted("rate limited")) is True

    def test_google_500_is_not_retriable(self):
        from google.api_core.exceptions import InternalServerError
        assert LLMRouter()._is_rate_limited(InternalServerError("server error")) is False

    def test_openai_rate_limit_is_retriable(self):
        import httpx
        import openai
        response = httpx.Response(
            429, request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        )
        exc = openai.RateLimitError("rate limit", response=response, body=None)
        assert LLMRouter()._is_rate_limited(exc) is True

    def test_openai_500_is_not_retriable(self):
        import httpx
        import openai
        response = httpx.Response(
            500, request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        )
        exc = openai.InternalServerError("server error", response=response, body=None)
        assert LLMRouter()._is_rate_limited(exc) is False

    def test_generic_exception_is_not_retriable(self):
        assert LLMRouter()._is_rate_limited(Exception("unknown")) is False
