from django.contrib import admin

from .models import LeadSubmission, LeadSubmissionImage, SodEstimate

class SodEstimateAdmin(admin.ModelAdmin):
    model = SodEstimate


class LeadSubmissionImageInline(admin.TabularInline):
    model = LeadSubmissionImage
    extra = 0
    readonly_fields = ('file', 'original_name', 'file_size', 'content_type', 'uploaded_at')
    can_delete = False


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'service', 'email', 'phone', 'email_status', 'email_attempts', 'email_next_attempt_at', 'emailed_at')
    list_filter = ('email_status', 'service', 'marketing', 'created_at')
    search_fields = ('name', 'email', 'phone', 'address', 'service', 'message')
    readonly_fields = (
        'created_at',
        'updated_at',
        'emailed_at',
        'email_error',
        'recipient_emails',
        'email_status',
        'email_attempts',
        'email_next_attempt_at',
        'email_claimed_at',
    )
    inlines = (LeadSubmissionImageInline,)
    actions = ('resend_lead_emails',)

    @admin.action(description='Queue selected lead emails for resending')
    def resend_lead_emails(self, request, queryset):
        from .lead_queue import queue_lead_emails

        count = queue_lead_emails(queryset)
        self.message_user(request, f"Queued {count} lead email(s). Emails already pending or sending were left in place.")


admin.site.register(SodEstimate)
