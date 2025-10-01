from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import (
    Post,
    Event,
    CaseStudy,
    Presentation,
    SiteSettings,
    ContactSubmission,
    NewsletterSubscription,
)
from .forms import ContactForm, NewsletterForm
import json


def get_site_context():
    """Get site-wide context data."""
    try:
        site_settings = SiteSettings.get_settings()
    except:
        site_settings = None

    return {
        "site_settings": site_settings,
    }


def home_view(request):
    """Home page view."""
    context = get_site_context()

    # Get featured/next event
    featured_event = Event.objects.filter(
        is_published=True, is_featured=True, starts_at__gte=timezone.now()
    ).first()

    # Get latest blog posts
    latest_posts = Post.objects.filter(
        is_published=True, publish_at__lte=timezone.now()
    )[:3]

    # Get featured presentations
    featured_presentations = Presentation.objects.filter(
        is_published=True, featured=True, publish_at__lte=timezone.now()
    )[:3]

    # Get featured case studies
    featured_cases = CaseStudy.objects.filter(
        is_published=True, featured=True, publish_at__lte=timezone.now()
    )[:3]

    context.update(
        {
            "featured_event": featured_event,
            "latest_posts": latest_posts,
            "featured_presentations": featured_presentations,
            "featured_cases": featured_cases,
        }
    )

    return render(request, "core/home.html", context)


def blog_list_view(request):
    """Blog listing page."""
    context = get_site_context()

    # Get search query
    search_query = request.GET.get("search", "")
    tag_filter = request.GET.get("tag", "")

    posts = Post.objects.filter(is_published=True, publish_at__lte=timezone.now())

    # Apply search filter
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(body__icontains=search_query)
        )

    # Apply tag filter
    if tag_filter:
        posts = posts.filter(tags__name__icontains=tag_filter)

    # Pagination
    paginator = Paginator(posts, 9)  # 9 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get all tags for filter
    all_tags = Post.tags.most_common()[:20]

    context.update(
        {
            "page_obj": page_obj,
            "search_query": search_query,
            "tag_filter": tag_filter,
            "all_tags": all_tags,
        }
    )

    return render(request, "core/blog_list.html", context)


def blog_detail_view(request, slug):
    """Blog post detail page."""
    context = get_site_context()

    post = get_object_or_404(
        Post.objects.filter(is_published=True, publish_at__lte=timezone.now()),
        slug=slug,
    )

    # Get related posts (same tags)
    related_posts = (
        Post.objects.filter(
            is_published=True, publish_at__lte=timezone.now(), tags__in=post.tags.all()
        )
        .exclude(pk=post.pk)
        .distinct()[:3]
    )

    context.update(
        {
            "post": post,
            "related_posts": related_posts,
        }
    )

    return render(request, "core/blog_detail.html", context)


def events_list_view(request):
    """Events listing page."""
    context = get_site_context()

    now = timezone.now()

    # Get upcoming events
    upcoming_events = Event.objects.filter(
        is_published=True, starts_at__gte=now
    ).order_by("starts_at")

    # Get past events
    past_events = Event.objects.filter(is_published=True, ends_at__lt=now).order_by(
        "-starts_at"
    )

    context.update(
        {
            "upcoming_events": upcoming_events,
            "past_events": past_events,
        }
    )

    return render(request, "core/events_list.html", context)


def event_detail_view(request, slug):
    """Event detail page."""
    context = get_site_context()

    event = get_object_or_404(Event.objects.filter(is_published=True), slug=slug)

    # Get related presentations for this event
    presentations = event.presentations.filter(
        is_published=True, publish_at__lte=timezone.now()
    )

    context.update(
        {
            "event": event,
            "presentations": presentations,
        }
    )

    return render(request, "core/event_detail.html", context)


def about_view(request):
    """About page view."""
    context = get_site_context()

    # Get featured presentations and case studies for showcasing
    featured_presentations = Presentation.objects.filter(
        is_published=True, publish_at__lte=timezone.now()
    )[:6]

    featured_cases = CaseStudy.objects.filter(
        is_published=True, publish_at__lte=timezone.now()
    )[:6]

    context.update(
        {
            "featured_presentations": featured_presentations,
            "featured_cases": featured_cases,
        }
    )

    return render(request, "core/about.html", context)


def contact_view(request):
    """Contact page view."""
    context = get_site_context()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact submission
            contact = ContactSubmission(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                subject=form.cleaned_data.get("subject", ""),
                message=form.cleaned_data["message"],
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            )
            contact.save()

            messages.success(
                request, "Thank you for your message! We will get back to you soon."
            )
            return redirect("core:contact")
    else:
        form = ContactForm()

    context.update(
        {
            "form": form,
        }
    )

    return render(request, "core/contact.html", context)


def newsletter_signup_view(request):
    """Newsletter signup AJAX view."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email", "").strip()

            if not email:
                return JsonResponse({"success": False, "error": "Email is required"})

            # Check if already subscribed
            subscription, created = NewsletterSubscription.objects.get_or_create(
                email=email, defaults={"ip_address": request.META.get("REMOTE_ADDR")}
            )

            if created:
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Thank you for subscribing to our newsletter!",
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "You are already subscribed to our newsletter.",
                    }
                )

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid request"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def case_study_detail_view(request, slug):
    """Case study detail page."""
    context = get_site_context()

    case_study = get_object_or_404(
        CaseStudy.objects.filter(is_published=True, publish_at__lte=timezone.now()),
        slug=slug,
    )

    # Get related case studies
    related_cases = (
        CaseStudy.objects.filter(
            is_published=True,
            publish_at__lte=timezone.now(),
            tags__in=case_study.tags.all(),
        )
        .exclude(pk=case_study.pk)
        .distinct()[:3]
    )

    context.update(
        {
            "case_study": case_study,
            "related_cases": related_cases,
        }
    )

    return render(request, "core/case_detail.html", context)


def presentation_detail_view(request, slug):
    """Presentation detail page."""
    context = get_site_context()

    presentation = get_object_or_404(
        Presentation.objects.filter(is_published=True, publish_at__lte=timezone.now()),
        slug=slug,
    )

    # Get related presentations
    related_presentations = (
        Presentation.objects.filter(
            is_published=True,
            publish_at__lte=timezone.now(),
            tags__in=presentation.tags.all(),
        )
        .exclude(pk=presentation.pk)
        .distinct()[:3]
    )

    context.update(
        {
            "presentation": presentation,
            "related_presentations": related_presentations,
        }
    )

    return render(request, "core/presentation_detail.html", context)


# RSS Feed for blog
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed


class BlogRSSFeed(Feed):
    title = "AI-Snakk Blog"
    link = "/blog/"
    description = (
        "Latest posts from AI-Snakk - Practical AI for Nordic business and tech"
    )
    feed_type = Rss201rev2Feed

    def items(self):
        return Post.objects.filter(is_published=True, publish_at__lte=timezone.now())[
            :10
        ]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.publish_at or item.created_at


# Sitemaps
class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True, publish_at__lte=timezone.now())

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Event.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            "core:home",
            "core:about",
            "core:contact",
            "core:blog_list",
            "core:events_list",
        ]

    def location(self, item):
        return reverse(item)
