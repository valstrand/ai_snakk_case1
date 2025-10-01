from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Post, Event, SiteSettings, ContactSubmission, NewsletterSubscription


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_site_settings_singleton(self):
        """Test that SiteSettings works as a singleton."""
        settings1 = SiteSettings.get_settings()
        settings2 = SiteSettings.get_settings()
        self.assertEqual(settings1.pk, settings2.pk)

    def test_post_slug_generation(self):
        """Test that post slug is auto-generated from title."""
        post = Post.objects.create(
            title="Test Blog Post",
            author=self.user,
            summary="Test summary",
            body="Test content",
            is_published=True,
        )
        self.assertEqual(post.slug, "test-blog-post")

    def test_event_featured_flag(self):
        """Test that only one event can be featured at a time."""
        event1 = Event.objects.create(
            title="Event 1",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            short_description="Test event 1",
            description="Test description 1",
            is_featured=True,
            is_published=True,
        )

        event2 = Event.objects.create(
            title="Event 2",
            starts_at=timezone.now() + timedelta(days=2),
            ends_at=timezone.now() + timedelta(days=2, hours=2),
            short_description="Test event 2",
            description="Test description 2",
            is_featured=True,
            is_published=True,
        )

        # Refresh from database
        event1.refresh_from_db()

        # Only event2 should be featured
        self.assertFalse(event1.is_featured)
        self.assertTrue(event2.is_featured)

    def test_post_absolute_url(self):
        """Test post absolute URL generation."""
        post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            summary="Test summary",
            body="Test content",
            is_published=True,
        )
        expected_url = reverse("core:blog_detail", kwargs={"slug": "test-post"})
        self.assertEqual(post.get_absolute_url(), expected_url)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_home_view(self):
        """Test that home page loads successfully."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI-Snakk")

    def test_blog_list_view(self):
        """Test blog listing page."""
        response = self.client.get(reverse("core:blog_list"))
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        """Test about page."""
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_get(self):
        """Test contact page GET request."""
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Get in Touch")

    def test_contact_view_post_valid(self):
        """Test contact form submission with valid data."""
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message content",
        }
        response = self.client.post(reverse("core:contact"), form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful submission

        # Check that submission was saved
        submission = ContactSubmission.objects.first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.name, "Test User")
        self.assertEqual(submission.email, "test@example.com")

    def test_contact_view_post_honeypot(self):
        """Test contact form honeypot spam protection."""
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message content",
            "honeypot": "spam",  # Should trigger spam detection
        }
        response = self.client.post(reverse("core:contact"), form_data)
        # Form should be invalid but still return 200 (form with errors)
        self.assertEqual(response.status_code, 200)

        # Check that no submission was saved
        self.assertEqual(ContactSubmission.objects.count(), 0)

    def test_events_list_view(self):
        """Test events listing page."""
        response = self.client.get(reverse("core:events_list"))
        self.assertEqual(response.status_code, 200)

    def test_newsletter_signup_ajax(self):
        """Test newsletter signup AJAX endpoint."""
        import json

        data = {"email": "test@example.com"}
        response = self.client.post(
            reverse("core:newsletter_signup"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])

        # Check that subscription was created
        subscription = NewsletterSubscription.objects.first()
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.email, "test@example.com")

    def test_newsletter_signup_duplicate(self):
        """Test newsletter signup with duplicate email."""
        import json

        # Create existing subscription
        NewsletterSubscription.objects.create(email="test@example.com")

        data = {"email": "test@example.com"}
        response = self.client.post(
            reverse("core:newsletter_signup"),
            json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["success"])
        self.assertIn("already subscribed", response_data["error"])

    def test_blog_post_detail_published(self):
        """Test that published blog posts are accessible."""
        post = Post.objects.create(
            title="Published Post",
            slug="published-post",
            author=self.user,
            summary="Test summary",
            body="Test content",
            is_published=True,
            publish_at=timezone.now() - timedelta(hours=1),  # Published in the past
        )

        response = self.client.get(
            reverse("core:blog_detail", kwargs={"slug": "published-post"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Post")

    def test_blog_post_detail_unpublished(self):
        """Test that unpublished blog posts return 404."""
        post = Post.objects.create(
            title="Unpublished Post",
            slug="unpublished-post",
            author=self.user,
            summary="Test summary",
            body="Test content",
            is_published=False,
        )

        response = self.client.get(
            reverse("core:blog_detail", kwargs={"slug": "unpublished-post"})
        )
        self.assertEqual(response.status_code, 404)


class SitemapTests(TestCase):
    def test_sitemap_accessibility(self):
        """Test that sitemap is accessible."""
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")


class AdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        self.client.login(username="admin", password="adminpass123")

    def test_admin_access(self):
        """Test that admin interface is accessible."""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_post_admin(self):
        """Test post admin interface."""
        response = self.client.get("/admin/core/post/")
        self.assertEqual(response.status_code, 200)

    def test_event_admin(self):
        """Test event admin interface."""
        response = self.client.get("/admin/core/event/")
        self.assertEqual(response.status_code, 200)
