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
    list_display = ('created_at', 'name', 'service', 'email', 'phone', 'email_status', 'emailed_at')
    list_filter = ('email_status', 'service', 'marketing', 'created_at')
    search_fields = ('name', 'email', 'phone', 'address', 'service', 'message')
    readonly_fields = (
        'created_at',
        'updated_at',
        'emailed_at',
        'email_error',
        'recipient_emails',
    )
    inlines = (LeadSubmissionImageInline,)
    actions = ('resend_lead_emails',)

    @admin.action(description='Resend selected lead emails')
    def resend_lead_emails(self, request, queryset):
        from mcexcavate.views import send_email_with_attachments

        sent_count = 0
        failed_count = 0
        for lead in queryset:
            file_paths = [image.absolute_path for image in lead.images.all()]
            try:
                send_email_with_attachments(lead.as_form_data(), file_paths, lead.source_page or lead.service)
            except Exception as exc:
                lead.mark_email_failed(exc)
                failed_count += 1
            else:
                lead.mark_email_sent()
                sent_count += 1

        self.message_user(request, f"Resent {sent_count} lead email(s). {failed_count} failed.")


admin.site.register(SodEstimate)
