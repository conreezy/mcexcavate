import smtplib
import socket
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .email_backend import IPv4EmailBackend, _IPv4SMTP, _IPv4SMTPSSL


class IPv4EmailBackendTests(SimpleTestCase):
    def test_resolves_ipv4_without_changing_tls_hostname(self):
        addresses = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.10', 587)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.11', 587)),
        ]
        connection = _IPv4SMTP(local_hostname='test.example')
        connection._host = 'smtp.gmail.com'
        connected_socket = Mock()
        with patch('socket.getaddrinfo', return_value=addresses) as resolve:
            with patch.object(
                smtplib.SMTP, '_get_socket',
                side_effect=[OSError('unreachable'), connected_socket],
            ) as connect:
                result = connection._get_socket('smtp.gmail.com', 587, 30)

        self.assertIs(result, connected_socket)
        resolve.assert_called_once_with(
            'smtp.gmail.com', 587, socket.AF_INET, socket.SOCK_STREAM
        )
        self.assertEqual(
            [call.args for call in connect.call_args_list],
            [('192.0.2.10', 587, 30), ('192.0.2.11', 587, 30)],
        )
        self.assertEqual(connection._host, 'smtp.gmail.com')

    def test_network_failures_remain_visible_to_queue_retry_handling(self):
        connection = _IPv4SMTP(local_hostname='test.example')
        addresses = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.10', 587)),
        ]
        failure = TimeoutError('SMTP connection timed out')
        with patch('socket.getaddrinfo', return_value=addresses):
            with patch.object(smtplib.SMTP, '_get_socket', side_effect=failure):
                with self.assertRaises(TimeoutError) as raised:
                    connection._get_socket('smtp.gmail.com', 587, 30)
        self.assertIs(raised.exception, failure)

    def test_backend_preserves_starttls_and_ssl_transport_selection(self):
        self.assertIs(
            IPv4EmailBackend(use_tls=True, use_ssl=False).connection_class,
            _IPv4SMTP,
        )
        self.assertIs(
            IPv4EmailBackend(use_tls=False, use_ssl=True).connection_class,
            _IPv4SMTPSSL,
        )
