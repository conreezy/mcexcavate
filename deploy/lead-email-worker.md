# Lead email worker

New contact/service enquiries save their compressed JPEG photos and lead/image rows before
returning confirmation. The rows are committed together with a due timestamp. The worker
polls every three seconds, claims one due lead with an atomic conditional update, and sends
the saved photos using the lead's recorded recipients. No Gmail call happens during the
form request or admin resend action. No extra queue server or package is required.

During form submission, photos are resized once to at most 1600 x 1600 (aspect ratio and EXIF orientation preserved)
and encoded once at JPEG quality 80, with 4:2:0 subsampling and no additional optimization
pass. Transparency is flattened onto white; animated uploads use their first frame.
Small images are not enlarged. Original bytes and EXIF/GPS metadata are not retained.
There is no new upload byte limit; the five-photo limit and Pillow's pixel safeguards remain.
An attachment budget of 12 MiB and encoded message budget of 20 MiB protect SMTP. Only if
either check detects an oversized email, the background worker reduces the saved photos
and rebuilds/rechecks the email. The successive maximum dimension/JPEG quality settings
are 1280/70, 960/60, 640/50, and 320/40; processing stops as soon as the email fits. This
never adds work to the customer's submission request. An email within budget, including
a later SMTP retry of an already reduced lead, does not reprocess photos.

Each smaller JPEG is written to a new path, then its database reference, byte size, and
content type are updated together before the previous file is removed. Originals remain
available if replacement creation or database updates fail. Replacements that are not
smaller are discarded. The worker refreshes/checks its claim while processing. SMTP uses
the exact files now referenced by the saved lead. Old photos may be reduced on an
explicitly queued historical resend, but historical leads are never queued automatically.

The fallback is bounded to four compression rounds per worker attempt. Unfixable message
text, invalid/missing photos, or an email still over budget after the final round remains
Failed for review; photos are never silently omitted. Only the pre-SMTP size checks
trigger compression. An SMTP rejection does not blindly shrink photos or resend an
ambiguously accepted message within the same attempt.

## Activation on the existing Linode

Deploy the reviewed application code and service file to `/home/conormc/mcexcavate`.
Run these steps from that directory during deployment (the application currently uses
Apache/mod_wsgi and Python 3.8):

1. Back up `src/db.sqlite3` using SQLite's backup API, and retain the previous code revision.
2. Run `./venv/bin/python src/manage.py migrate` and `./venv/bin/python src/manage.py check`.
3. Verify that the `conormc` service account can read the project `.env`, compressed uploads,
   and read/write both the SQLite database and its containing directory. Use the same
   database and media directory as Apache. Adjust the service user if the deployed app's
   ownership differs.
   The service uses group `www-data` and umask `0002` so files it creates remain
   accessible to Apache. Keep the database/upload directories setgid for that group.
4. Set `DJANGO_EMAIL_HOST_USER=info@crusaderconcrete.ca` in the server `.env`, and update
   `DJANGO_EMAIL_HOST_PASSWORD` with the Google app password for that account.
   Keep the value out of Git and terminal output. The worker reads the existing `.env`
   through Django settings; an inherited environment variable overrides that file.
   SMTP resolves Gmail's IPv4 addresses on each connection because Google rejected
   this Linode's login over IPv6 while accepting the same credentials over IPv4.
   The custom email backend retains the Gmail hostname for TLS and does not change
   networking for other parts of the site.
5. Install and start the service:

   ```sh
   sudo install -m 0644 deploy/mcexcavate-lead-email.service /etc/systemd/system/mcexcavate-lead-email.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now mcexcavate-lead-email
   sudo systemctl reload apache2
   sudo systemctl status mcexcavate-lead-email --no-pager
   ```

6. After authorization for a live test, submit one labelled test enquiry with photos.
   Confirm the response doesn't wait for email, the saved files are JPEGs no larger than
   1600 pixels on either edge, status advances from Pending to Sent, and both recipient
   inboxes receive the photos. "Sent" means accepted by SMTP, not confirmed inbox delivery.

The migration leaves every existing lead unqueued, including historical Pending/Failed
rows. It does not resend old enquiries automatically. Review failed leads in Django admin
and use **Queue selected lead emails for resending** when ready. Repeated clicks do not
reset a pending/sending job. This resets the attempt count for a selected completed/failed
job and does not send mail from the admin request.

## Retries and operations

- Temporary SMTP/network failures retry after 1, 5, then 15 minutes (four attempts total).
- Authentication failures, permanent SMTP rejections, missing attachments, and message
  size violations remain Failed for attention. A password failure does not loop on that
  lead. New leads still make their own first attempt.
- A claimed job whose worker disappeared can be reclaimed after ten minutes. The SMTP
  socket timeout is 30 seconds; graceful service shutdown allows 120 seconds to finish.
- Queue data survives restarts. SMTP cannot provide exactly-once delivery: a crash after
  acceptance but before recording Sent may lead to a duplicate on recovery. Claims stop
  ordinary simultaneous processing, and claim tokens stop old workers overwriting newer
  status. If a send is interrupted at an ambiguous point, check inboxes before resending.
- Inspect `email_error`, attempt count, and next attempt in admin. Logs are available via
  `sudo journalctl -u mcexcavate-lead-email --since today`. Check service health and aged
  Pending/Failed leads operationally; no separate alerting integration is installed.
- After changing `.env` credentials, run `sudo systemctl restart mcexcavate-lead-email`
  and reload Apache. Then explicitly queue the failed leads you want retried.
- `./venv/bin/python src/manage.py send_lead_emails --once` sends at most one due email;
  it is a real send, not a dry run. Use mocked/local-memory email backends for tests.

## Rollback

Stop/disable the worker before reverting to synchronous application code. Review any
pending/sending leads first: older code cannot deliver those queued notifications.
Do not leave migration 0004 in place with the older form code: its inserts omit the
new non-null attempt counter and would fail.

Before the new application has accepted any submissions, an activation rollback can
keep Apache stopped, reverse the project migration to 0003, restore the previous code
and SMTP settings, and restart Apache. After the new application has accepted submissions,
prefer a forward fix or a release that preserves the queue schema and processing. Do
not reverse the queue migration without preserving/reconciling queued jobs, and never
restore an old database over newly received leads.
