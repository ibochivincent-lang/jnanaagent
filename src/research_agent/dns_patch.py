"""DNS patch to provide reliable resolution for AWS ALB endpoints on Windows networks."""

import logging
import socket

log = logging.getLogger("research_agent.dns")

_STATIC_HOSTS = {
    "api.crustdata.com": "16.59.190.106",
    "litellm.vision.aivar.app": "32.194.119.88",
    "ingest.neatlogs.com": "35.166.158.209",
    "app.neatlogs.com": "35.166.158.209",
}

_ORIG_GETADDRINFO = socket.getaddrinfo


def _patched_getaddrinfo(host, port, *args, **kwargs):
    if host in _STATIC_HOSTS:
        target_ip = _STATIC_HOSTS[host]
        try:
            return _ORIG_GETADDRINFO(target_ip, port, *args, **kwargs)
        except Exception:
            pass
    return _ORIG_GETADDRINFO(host, port, *args, **kwargs)


# Apply patch globally
socket.getaddrinfo = _patched_getaddrinfo
