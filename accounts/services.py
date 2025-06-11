import random, redis
from django.conf import settings
import logging

r = redis.from_url(settings.REDIS_URL)
log = logging.getLogger(__name__) 

def generate_otp(phone: str) -> str:
    """
    Returns a 6-digit code and stores it in Redis with 5-minute TTL.
    """
    code = f"{random.randint(0, 999999):06}"
    r.setex(f"otp:{phone}", 600, code)
    log.warning("DEBUG-OTP  phone=%s  code=%s", phone, code)
    return code

def verify_otp(phone: str, code: str) -> bool:
    stored = r.get(f"otp:{phone}")
    return stored is not None and stored.decode() == code
