"""Use Gmail's IPv4 endpoints for this server's SMTP connections."""

import smtplib
import socket

from django.core.mail.backends.smtp import EmailBackend


class _IPv4Connection:
    def _get_socket(self, host, port, timeout):
        # Google accepts this Linode's credentials over IPv4 but rejects the
        # same login over IPv6. Resolve each connection; don't pin a Google IP
        # or change DNS/socket behavior for the rest of the application.
        addresses = socket.getaddrinfo(
            host, port, socket.AF_INET, socket.SOCK_STREAM
        )
        last_error = OSError("No IPv4 SMTP address found")
        for family, socktype, proto, canonical_name, address in addresses:
            try:
                # Keep self._host as the original hostname for TLS/SNI.
                return super()._get_socket(address[0], port, timeout)
            except OSError as error:
                last_error = error
        raise last_error


class _IPv4SMTP(_IPv4Connection, smtplib.SMTP):
    pass


class _IPv4SMTPSSL(_IPv4Connection, smtplib.SMTP_SSL):
    pass


class IPv4EmailBackend(EmailBackend):
    @property
    def connection_class(self):
        return _IPv4SMTPSSL if self.use_ssl else _IPv4SMTP
