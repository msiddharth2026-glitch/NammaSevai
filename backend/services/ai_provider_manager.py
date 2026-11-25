import time
import logging
import threading
from typing import Dict, Any, Optional, List, Tuple
from ..config import settings
from .providers.base_provider import BaseAIProvider, sanitize_secret_in_error
from .providers.openai_provider import OpenAIProvider
from .providers.grok_provider import GrokProvider
from .providers.gemini_provider import GeminiProvider

logger = logging.getLogger("nammasevai.provider_manager")

class CircuitState:
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Cooling down; skip immediately
    HALF_OPEN = "HALF_OPEN"# Testing with one request

class ProviderHealth:
    def __init__(self, name: str):
        self.name = name
        self.circuit_state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time = 0.0
        self.total_calls = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_error = None
        self.total_latency_ms = 0.0

    def average_latency_ms(self) -> float:
        if self.success_count == 0:
            return 0.0
        return round(self.total_latency_ms / self.success_count, 1)

class AIProviderManager:
    """
    Orchestrates multi-provider AI execution in strict priority order:
    1. ChatGPT / OpenAI (Primary)
    2. Grok / xAI (Secondary Fallback)
    3. Google Gemini (Final LLM Fallback)
    4. Deterministic Safe Rule Engine (Zero-Failure Fallback)

    Includes circuit breaker, cooldown tracking, latency metrics, and safe status reporting.
    """

    def __init__(self):
        self.timeout = settings.AI_PROVIDER_TIMEOUT_SECONDS
        self.cooldown_seconds = settings.AI_CIRCUIT_BREAKER_COOLDOWN_SECONDS
        self.failure_threshold = settings.AI_CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self._lock = threading.Lock()

        # Initialize provider instances in strict priority order
        self.openai_provider = OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            timeout=self.timeout
        )
        self.grok_provider = GrokProvider(
            api_key=settings.XAI_API_KEY,
            model=settings.XAI_MODEL,
            timeout=self.timeout
        )
        self.gemini_provider = GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            timeout=self.timeout
        )

        self.providers: List[BaseAIProvider] = [
            self.openai_provider,
            self.grok_provider,
            self.gemini_provider
        ]

        self.health: Dict[str, ProviderHealth] = {
            p.name: ProviderHealth(p.name) for p in self.providers
        }
        self.health["rule_engine"] = ProviderHealth("rule_engine")

        self.total_requests = 0
        self.fallback_events = 0
        self.last_used_provider = "rule_engine"

    def reload_config(self):
        """Allows hot-reloading keys and settings from settings/env."""
        with self._lock:
            self.openai_provider = OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                timeout=settings.AI_PROVIDER_TIMEOUT_SECONDS
            )
            self.grok_provider = GrokProvider(
                api_key=settings.XAI_API_KEY,
                model=settings.XAI_MODEL,
                timeout=settings.AI_PROVIDER_TIMEOUT_SECONDS
            )
            self.gemini_provider = GeminiProvider(
                api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL,
                timeout=settings.AI_PROVIDER_TIMEOUT_SECONDS
            )
            self.providers = [
                self.openai_provider,
                self.grok_provider,
                self.gemini_provider
            ]

    def _should_attempt_provider(self, provider: BaseAIProvider) -> Tuple[bool, str]:
        """Checks if a provider is configured and available via circuit breaker."""
        if not provider.is_configured():
            return False, "unconfigured"

        h = self.health[provider.name]
        now = time.time()

        if h.circuit_state == CircuitState.OPEN:
            if now - h.last_failure_time >= self.cooldown_seconds:
                h.circuit_state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker for {provider.name} changed from OPEN to HALF_OPEN (cooldown expired).")
                return True, "half_open_trial"
            else:
                remaining = int(self.cooldown_seconds - (now - h.last_failure_time))
                return False, f"circuit_open (cooldown {remaining}s remaining)"

        return True, "ready"

    def _record_success(self, provider_name: str, latency_ms: float):
        with self._lock:
            h = self.health[provider_name]
            h.total_calls += 1
            h.success_count += 1
            h.total_latency_ms += latency_ms
            h.consecutive_failures = 0
            if h.circuit_state != CircuitState.CLOSED:
                logger.info(f"Circuit breaker for {provider_name} reset to CLOSED after successful request.")
                h.circuit_state = CircuitState.CLOSED
            self.last_used_provider = provider_name

    def _record_failure(self, provider_name: str, error_msg: str):
        with self._lock:
            h = self.health[provider_name]
            h.total_calls += 1
            h.failure_count += 1
            h.consecutive_failures += 1
            h.last_failure_time = time.time()
            h.last_error = sanitize_secret_in_error(error_msg)

            if h.consecutive_failures >= self.failure_threshold and h.circuit_state != CircuitState.OPEN:
                h.circuit_state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker for {provider_name} TRIPPED to OPEN after {h.consecutive_failures} "
                    f"consecutive failures. Cooling down for {self.cooldown_seconds}s."
                )

    def analyze_query(self, text: str, lang: str = "ta") -> Tuple[Optional[Dict[str, Any]], str, List[Dict[str, str]]]:
        """
        Executes query analysis across providers in strict priority sequence:
        OpenAI -> Grok -> Gemini -> (None for rule engine fallback).

        Returns:
            (extracted_json_or_none, provider_name_used, fallback_history)
        """
        with self._lock:
            self.total_requests += 1

        fallback_history: List[Dict[str, str]] = []

        for provider in self.providers:
            should_attempt, reason = self._should_attempt_provider(provider)
            if not should_attempt:
                fallback_history.append({
                    "provider": provider.name,
                    "status": "skipped",
                    "reason": reason
                })
                continue

            start_t = time.time()
            try:
                logger.info(f"Attempting query analysis with primary/active provider: {provider.display_name}")
                result = provider.analyze_query(text, lang)
                if result and isinstance(result, dict):
                    latency_ms = (time.time() - start_t) * 1000
                    self._record_success(provider.name, latency_ms)
                    logger.info(f"Provider {provider.name} successfully analyzed query in {round(latency_ms, 1)}ms")
                    return result, provider.name, fallback_history
                else:
                    raise ValueError(f"{provider.name} returned empty or invalid non-dict response")
            except Exception as e:
                err_msg = sanitize_secret_in_error(str(e))
                self._record_failure(provider.name, err_msg)
                with self._lock:
                    self.fallback_events += 1
                fallback_history.append({
                    "provider": provider.name,
                    "status": "failed",
                    "reason": err_msg
                })
                logger.warning(
                    f"AI Provider {provider.name} failed ({err_msg}). Cascading to next available provider."
                )

        # All LLM providers failed or were unconfigured
        with self._lock:
            self.health["rule_engine"].total_calls += 1
            self.health["rule_engine"].success_count += 1
            self.last_used_provider = "rule_engine"

        logger.info("All configured AI providers unavailable. Gracefully falling back to deterministic Rule Engine.")
        return None, "rule_engine", fallback_history

    def generate_response(
        self, 
        query: str, 
        matches: list, 
        missing_info: list, 
        lang: str = "ta"
    ) -> Tuple[Optional[str], str, List[Dict[str, str]]]:
        """
        Generates compassionate summary text across providers in strict priority sequence.
        Returns:
            (response_text_or_none, provider_name_used, fallback_history)
        """
        fallback_history: List[Dict[str, str]] = []

        for provider in self.providers:
            should_attempt, reason = self._should_attempt_provider(provider)
            if not should_attempt:
                fallback_history.append({
                    "provider": provider.name,
                    "status": "skipped",
                    "reason": reason
                })
                continue

            start_t = time.time()
            try:
                result = provider.generate_response(query, matches, missing_info, lang)
                if result and isinstance(result, str) and result.strip():
                    latency_ms = (time.time() - start_t) * 1000
                    self._record_success(provider.name, latency_ms)
                    return result.strip(), provider.name, fallback_history
                else:
                    raise ValueError(f"{provider.name} returned empty response text")
            except Exception as e:
                err_msg = sanitize_secret_in_error(str(e))
                self._record_failure(provider.name, err_msg)
                with self._lock:
                    self.fallback_events += 1
                fallback_history.append({
                    "provider": provider.name,
                    "status": "failed",
                    "reason": err_msg
                })

        return None, "rule_engine", fallback_history

    def get_safe_status(self) -> Dict[str, Any]:
        """
        Returns provider health, metrics, and circuit status without exposing any API keys.
        Safe for consumption by admin dashboards and monitoring tools.
        """
        provider_details = []
        for p in self.providers:
            h = self.health[p.name]
            is_cfg = p.is_configured()

            # Determine human-readable status
            if not is_cfg:
                status_label = "unconfigured"
            elif h.circuit_state == CircuitState.OPEN:
                status_label = "circuit_open"
            elif h.consecutive_failures > 0:
                status_label = "degraded"
            else:
                status_label = "operational"

            provider_details.append({
                "name": p.name,
                "display_name": p.display_name,
                "priority": p.priority,
                "model": p.model,
                "is_configured": is_cfg,
                "status": status_label,
                "circuit_state": h.circuit_state,
                "consecutive_failures": h.consecutive_failures,
                "total_calls": h.total_calls,
                "success_count": h.success_count,
                "failure_count": h.failure_count,
                "average_latency_ms": h.average_latency_ms(),
                "last_error": h.last_error
            })

        # Rule engine fallback status
        r_health = self.health["rule_engine"]
        provider_details.append({
            "name": "rule_engine",
            "display_name": "Deterministic Rule Engine (Safe Fallback)",
            "priority": 4,
            "model": "nlp-rule-extractor-v2",
            "is_configured": True,
            "status": "operational",
            "circuit_state": "CLOSED",
            "consecutive_failures": 0,
            "total_calls": r_health.total_calls,
            "success_count": r_health.success_count,
            "failure_count": 0,
            "average_latency_ms": 0.5,
            "last_error": None
        })

        # Overall health
        operational_count = sum(1 for p in provider_details if p["status"] == "operational" and p["name"] != "rule_engine")
        overall = "operational" if operational_count > 0 else "fallback_only"

        return {
            "overall_status": overall,
            "current_active_provider": self.last_used_provider,
            "priority_order": ["openai", "grok", "gemini", "rule_engine"],
            "total_requests": self.total_requests,
            "fallback_events": self.fallback_events,
            "circuit_cooldown_seconds": self.cooldown_seconds,
            "failure_threshold": self.failure_threshold,
            "providers": provider_details
        }

# Global singleton manager instance
ai_provider_manager = AIProviderManager()
