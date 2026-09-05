import logging
import signal
from threading import Event

from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, close_old_connections

from project.lead_queue import process_next_lead_email


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send queued lead notifications; run as the dedicated email worker service.'

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='Process at most one due email, then exit.')
        parser.add_argument('--poll-interval', type=float, default=3.0, help='Seconds between idle queue checks.')

    def handle(self, *args, **options):
        if options['poll_interval'] <= 0:
            raise CommandError('--poll-interval must be positive.')
        if options['once']:
            processed = process_next_lead_email()
            self.stdout.write('Processed one email.' if processed else 'No email is due.')
            return

        stopped = Event()
        previous_handlers = {}
        for sig in (signal.SIGTERM, signal.SIGINT):
            previous_handlers[sig] = signal.signal(sig, lambda signum, frame: stopped.set())
        self.stdout.write('Lead email worker started.')
        try:
            while not stopped.is_set():
                close_old_connections()
                try:
                    processed = process_next_lead_email()
                except OperationalError:
                    logger.exception('Database unavailable; email worker will check again.')
                    processed = False
                if not processed:
                    stopped.wait(options['poll_interval'])
        finally:
            for sig, handler in previous_handlers.items():
                signal.signal(sig, handler)
            close_old_connections()
            self.stdout.write('Lead email worker stopped.')
