from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    SiteSettings,
    Post,
    Event,
    CaseStudy,
    Presentation,
    ContactSubmission,
    NewsletterSubscription,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["brand_name", "contact_email", "created_at"]
    fieldsets = (
        (
            "Basic Info",
            {"fields": ("brand_name", "logo_image", "tagline", "description")},
        ),
        (
            "Contact & Social",
            {
                "fields": (
                    "contact_email",
                    "twitter_url",
                    "linkedin_url",
                    "facebook_url",
                    "github_url",
                )
            },
        ),
        ("Newsletter & Analytics", {"fields": ("newsletter_provider", "analytics_id")}),
    )

    def has_add_permission(self, request):
        # Limit to one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "is_published",
        "featured",
        "publish_at",
        "created_at",
    ]
    list_filter = ["is_published", "featured", "tags", "created_at", "author"]
    search_fields = ["title", "summary", "body"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["is_published", "featured"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "summary",
                    "body",
                    "cover_image",
                    "tags",
                )
            },
        ),
        (
            "Publishing",
            {"fields": ("is_published", "publish_at", "featured", "reading_time")},
        ),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "starts_at",
        "location",
        "is_featured",
        "is_published",
        "created_at",
    ]
    list_filter = ["is_published", "is_featured", "starts_at", "tags"]
    search_fields = ["title", "short_description", "description"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["is_published", "is_featured"]
    date_hierarchy = "starts_at"

    fieldsets = (
        (
            "Event Details",
            {
                "fields": (
                    "title",
                    "slug",
                    "short_description",
                    "description",
                    "hero_image",
                    "tags",
                )
            },
        ),
        (
            "Date & Location",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                    "timezone",
                    "location",
                    "streaming_url",
                )
            },
        ),
        ("Event Management", {"fields": ("is_featured", "capacity", "rsvp_url")}),
        ("Publishing", {"fields": ("is_published", "publish_at")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "client",
        "industry",
        "featured",
        "is_published",
        "created_at",
    ]
    list_filter = ["is_published", "featured", "industry", "tags", "created_at"]
    search_fields = ["title", "client", "summary", "body"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["is_published", "featured"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Case Study Details",
            {
                "fields": (
                    "title",
                    "slug",
                    "client",
                    "industry",
                    "summary",
                    "body",
                    "cover_image",
                    "tags",
                )
            },
        ),
        (
            "Results & Metrics",
            {"fields": ("roi_percentage", "cost_savings", "time_savings")},
        ),
        ("Publishing", {"fields": ("is_published", "publish_at", "featured")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "speaker",
        "presentation_date",
        "event",
        "featured",
        "is_published",
    ]
    list_filter = ["is_published", "featured", "presentation_date", "tags", "event"]
    search_fields = ["title", "speaker", "summary", "body"]
    prepopulated_fields = {"slug": ("title", "speaker")}
    list_editable = ["is_published", "featured"]
    date_hierarchy = "presentation_date"

    fieldsets = (
        (
            "Presentation Details",
            {"fields": ("title", "slug", "summary", "body", "cover_image", "tags")},
        ),
        ("Speaker Info", {"fields": ("speaker", "speaker_title", "speaker_bio")}),
        (
            "Resources",
            {"fields": ("slides_url", "video_url", "event", "presentation_date")},
        ),
        ("Publishing", {"fields": ("is_published", "publish_at", "featured")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("event")


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = [
        "name",
        "email",
        "subject",
        "message",
        "ip_address",
        "user_agent",
        "created_at",
    ]
    list_editable = ["is_read"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Contact Info", {"fields": ("name", "email", "subject")}),
        ("Message", {"fields": ("message",)}),
        (
            "Meta",
            {
                "fields": ("ip_address", "user_agent", "is_read", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["email", "is_active", "confirmed_at", "created_at"]
    list_filter = ["is_active", "confirmed_at", "created_at"]
    search_fields = ["email"]
    readonly_fields = ["email", "ip_address", "created_at"]
    list_editable = ["is_active"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Subscription Info", {"fields": ("email", "is_active", "confirmed_at")}),
        ("Meta", {"fields": ("ip_address", "created_at"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return False


# Customize admin site header and title
admin.site.site_header = "AI-Snakk Admin"
admin.site.site_title = "AI-Snakk Admin"
admin.site.index_title = "Welcome to AI-Snakk Administration"
