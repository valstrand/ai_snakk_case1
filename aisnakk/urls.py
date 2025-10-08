"""
URL configuration for aisnakk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from core.views import (
    PostSitemap,
    EventSitemap,
    StaticSitemap,
    CaseStudySitemap,
    PresentationSitemap,
    BlogRSSFeed,
)

# Sitemaps
sitemaps = {
    "posts": PostSitemap,
    "events": EventSitemap,
    "cases": CaseStudySitemap,
    "presentations": PresentationSitemap,
    "static": StaticSitemap,
}


def robots_txt(request):
    content = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://ai-snakk.no/sitemap.xml

# Disallow admin and private areas
Disallow: /admin/
Disallow: /ckeditor5/
Disallow: /static/admin/
Disallow: /media/

# Allow important pages
Allow: /blog/
Allow: /events/
Allow: /about/
Allow: /contact/"""
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("blog/rss.xml", BlogRSSFeed(), name="blog_rss"),
    path("", include("core.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
