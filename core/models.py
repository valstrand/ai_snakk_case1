from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
import pytz


class TimeStampedModel(models.Model):
    """Abstract base model with created_at and updated_at fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SEOModel(models.Model):
    """Abstract base model with SEO fields."""

    seo_title = models.CharField(
        max_length=60, blank=True, help_text="SEO title (max 60 chars)"
    )
    seo_description = models.TextField(
        max_length=160, blank=True, help_text="SEO description (max 160 chars)"
    )

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Abstract base model for publishable content."""

    is_published = models.BooleanField(
        default=False, help_text="Check to publish this content"
    )
    publish_at = models.DateTimeField(
        blank=True, null=True, help_text="Schedule publication date/time"
    )

    class Meta:
        abstract = True

    def is_published_now(self):
        """Check if content should be published at current time."""
        if not self.is_published:
            return False
        if self.publish_at and self.publish_at > timezone.now():
            return False
        return True


class SiteSettings(TimeStampedModel):
    """Site-wide configuration settings."""

    brand_name = models.CharField(max_length=100, default="AI-Snakk")
    logo_image = models.ImageField(upload_to="site/", blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    # Social links
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    # Contact info
    contact_email = models.EmailField(blank=True)
    newsletter_provider = models.CharField(
        max_length=100, blank=True, help_text="Newsletter service provider"
    )

    # Analytics
    analytics_id = models.CharField(
        max_length=50, blank=True, help_text="Google Analytics or Plausible ID"
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.brand_name

    @classmethod
    def get_settings(cls):
        """Get site settings singleton."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Post(TimeStampedModel, SEOModel, PublishableModel):
    """Blog post model."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    summary = models.TextField(
        max_length=300, help_text="Brief description of the post"
    )
    body = RichTextField()
    cover_image = models.ImageField(upload_to="posts/", blank=True, null=True)
    tags = TaggableManager(blank=True)
    featured = models.BooleanField(
        default=False, help_text="Feature this post on homepage"
    )
    reading_time = models.PositiveIntegerField(
        default=5, help_text="Estimated reading time in minutes"
    )

    class Meta:
        ordering = ["-publish_at", "-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.publish_at and self.is_published:
            self.publish_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:blog_detail", kwargs={"slug": self.slug})

    def get_seo_title(self):
        return self.seo_title or self.title

    def get_seo_description(self):
        return self.seo_description or self.summary


class Event(TimeStampedModel, SEOModel, PublishableModel):
    """Event model."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    timezone = models.CharField(
        max_length=50,
        default="Europe/Oslo",
        choices=[(tz, tz) for tz in pytz.common_timezones],
    )
    location = models.CharField(
        max_length=200, blank=True, help_text="Physical location"
    )
    streaming_url = models.URLField(
        blank=True, help_text="Online meeting/streaming link"
    )
    short_description = models.TextField(
        max_length=300, help_text="Brief description for listings"
    )
    description = RichTextField(help_text="Full event description")
    hero_image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_featured = models.BooleanField(
        default=False, help_text="Mark as featured/next event (only one allowed)"
    )
    rsvp_url = models.URLField(blank=True, help_text="External RSVP/ticketing link")
    capacity = models.PositiveIntegerField(
        blank=True, null=True, help_text="Event capacity"
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["starts_at"]
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return f"{self.title} - {self.starts_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Ensure only one featured event
        if self.is_featured:
            Event.objects.filter(is_featured=True).exclude(pk=self.pk).update(
                is_featured=False
            )

        if not self.publish_at and self.is_published:
            self.publish_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:event_detail", kwargs={"slug": self.slug})

    def get_seo_title(self):
        return self.seo_title or self.title

    def get_seo_description(self):
        return self.seo_description or self.short_description

    @property
    def is_upcoming(self):
        return self.starts_at > timezone.now()

    @property
    def is_past(self):
        return self.ends_at < timezone.now()

    @property
    def local_start_time(self):
        """Get start time in event's timezone."""
        tz = pytz.timezone(self.timezone)
        return self.starts_at.astimezone(tz)

    @property
    def local_end_time(self):
        """Get end time in event's timezone."""
        tz = pytz.timezone(self.timezone)
        return self.ends_at.astimezone(tz)


class CaseStudy(TimeStampedModel, SEOModel, PublishableModel):
    """Case study model."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    client = models.CharField(
        max_length=100, blank=True, help_text="Client or company name"
    )
    industry = models.CharField(max_length=100, blank=True)
    summary = models.TextField(
        max_length=300, help_text="Brief description of the case study"
    )
    body = RichTextField()
    cover_image = models.ImageField(upload_to="cases/", blank=True, null=True)
    tags = TaggableManager(blank=True)
    featured = models.BooleanField(
        default=False, help_text="Feature this case study on homepage"
    )

    # Results/metrics
    roi_percentage = models.PositiveIntegerField(
        blank=True, null=True, help_text="ROI percentage"
    )
    cost_savings = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    time_savings = models.CharField(
        max_length=100, blank=True, help_text="e.g., '50% reduction in processing time'"
    )

    class Meta:
        ordering = ["-publish_at", "-created_at"]
        verbose_name = "Case Study"
        verbose_name_plural = "Case Studies"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.publish_at and self.is_published:
            self.publish_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:case_detail", kwargs={"slug": self.slug})

    def get_seo_title(self):
        return self.seo_title or self.title

    def get_seo_description(self):
        return self.seo_description or self.summary


class Presentation(TimeStampedModel, SEOModel, PublishableModel):
    """Presentation/talk model."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    speaker = models.CharField(max_length=100, help_text="Speaker name")
    speaker_title = models.CharField(
        max_length=200, blank=True, help_text="Speaker title/role"
    )
    speaker_bio = models.TextField(blank=True)
    summary = models.TextField(
        max_length=300, help_text="Brief description of the presentation"
    )
    body = RichTextField(blank=True, help_text="Full presentation description/notes")
    cover_image = models.ImageField(upload_to="presentations/", blank=True, null=True)
    slides_url = models.URLField(blank=True, help_text="Link to slides")
    video_url = models.URLField(blank=True, help_text="Link to video recording")
    tags = TaggableManager(blank=True)
    featured = models.BooleanField(
        default=False, help_text="Feature this presentation on homepage"
    )

    # Event relationship
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="presentations",
    )
    presentation_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-presentation_date", "-publish_at", "-created_at"]
        verbose_name = "Presentation"
        verbose_name_plural = "Presentations"

    def __str__(self):
        return f"{self.title} by {self.speaker}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.speaker}")
        if not self.publish_at and self.is_published:
            self.publish_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:presentation_detail", kwargs={"slug": self.slug})

    def get_seo_title(self):
        return self.seo_title or f"{self.title} by {self.speaker}"

    def get_seo_description(self):
        return self.seo_description or self.summary


class ContactSubmission(TimeStampedModel):
    """Contact form submission model."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"

    def __str__(self):
        return f"{self.name} - {self.email} ({self.created_at.strftime('%Y-%m-%d')})"


class NewsletterSubscription(TimeStampedModel):
    """Newsletter subscription model."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"

    def __str__(self):
        return self.email
