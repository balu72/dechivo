"""
Mixpanel Analytics for Backend
Tracks: API processing time, errors, enhancement success rate
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Mixpanel client
mp = None

# Same token as frontend - EU data residency
MIXPANEL_TOKEN = os.getenv('MIXPANEL_TOKEN', 'c2c3389649cc7cfc0c632360812e2e7c')

try:
    from mixpanel import Mixpanel
    mp = Mixpanel(MIXPANEL_TOKEN, api_host='api-eu.mixpanel.com')
    logger.info("✅ Mixpanel backend analytics initialized")
except ImportError:
    logger.warning("⚠️ Mixpanel package not installed, analytics disabled")
except Exception as e:
    logger.warning(f"⚠️ Mixpanel initialization failed: {e}")


def track_event(distinct_id: str, event_name: str, properties: dict = None):
    """
    Track an event in Mixpanel
    
    Args:
        distinct_id: User ID or anonymous ID
        event_name: Name of the event
        properties: Additional event properties
    """
    if not mp:
        return
    
    try:
        event_props = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'backend',
            **(properties or {})
        }
        mp.track(distinct_id, event_name, event_props)
        logger.debug(f"📊 Analytics: {event_name} for {distinct_id}")
    except Exception as e:
        logger.error(f"Analytics error: {e}")


def track_enhancement_request(user_id: str, jd_length: int, has_org_context: bool):
    """Track when an enhancement request is received"""
    track_event(user_id, 'Enhancement Request', {
        'jd_length': jd_length,
        'has_org_context': has_org_context
    })


def track_enhancement_success(
    user_id: str, 
    skills_count: int, 
    duration_ms: int,
    llm_provider: str,
    kg_connected: bool
):
    """Track successful enhancement"""
    track_event(user_id, 'Enhancement Success', {
        'skills_count': skills_count,
        'duration_ms': duration_ms,
        'duration_seconds': round(duration_ms / 1000, 2),
        'llm_provider': llm_provider,
        'kg_connected': kg_connected,
        'status': 'success'
    })


def track_enhancement_failure(user_id: str, error: str, duration_ms: int = 0):
    """Track failed enhancement"""
    track_event(user_id, 'Enhancement Failure', {
        'error': error[:200],  # Truncate error message
        'duration_ms': duration_ms,
        'status': 'failure'
    })


def track_api_error(user_id: str, endpoint: str, error: str, status_code: int = 500):
    """Track API errors"""
    track_event(user_id, 'API Error', {
        'endpoint': endpoint,
        'error': error[:200],
        'status_code': status_code
    })


def track_llm_usage(
    user_id: str, 
    provider: str, 
    model: str, 
    input_tokens: int = 0, 
    output_tokens: int = 0,
    latency_ms: int = 0
):
    """Track LLM API usage"""
    track_event(user_id, 'LLM Usage', {
        'provider': provider,
        'model': model,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'latency_ms': latency_ms
    })


def set_user_profile(user_id: str, properties: dict):
    """Set user profile properties"""
    if not mp:
        return
    
    try:
        mp.people_set(user_id, properties)
    except Exception as e:
        logger.error(f"Analytics profile error: {e}")
