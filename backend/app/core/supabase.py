"""
Supabase client factory.
Provides two clients:
  - anon_client  : limited permissions (for user-facing operations)
  - admin_client : service-role key (for server-side privileged operations)
"""

import logging
from functools import lru_cache

from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Return a cached Supabase anon client."""
    logger.debug("Initialising Supabase anon client")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@lru_cache(maxsize=1)
def get_supabase_admin() -> Client:
    """Return a cached Supabase admin (service-role) client."""
    logger.debug("Initialising Supabase admin client")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
