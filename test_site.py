#!/usr/bin/env python
"""
Simple test script to verify the Django site is working properly.
"""

import os
import sys
import django

# Setup Django first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aisnakk.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User


def test_basic_functionality():
    """Test basic site functionality."""
    client = Client()

    print("Testing AI-Snakk Website...")

    # Test home page
    response = client.get("/")
    print(f"✓ Home page: {response.status_code} (expected 200)")
    assert response.status_code == 200

    # Test blog page
    response = client.get("/blog/")
    print(f"✓ Blog page: {response.status_code} (expected 200)")
    assert response.status_code == 200

    # Test events page
    response = client.get("/events/")
    print(f"✓ Events page: {response.status_code} (expected 200)")
    assert response.status_code == 200

    # Test about page
    response = client.get("/about/")
    print(f"✓ About page: {response.status_code} (expected 200)")
    assert response.status_code == 200

    # Test contact page
    response = client.get("/contact/")
    print(f"✓ Contact page: {response.status_code} (expected 200)")
    assert response.status_code == 200

    # Test admin page
    response = client.get("/admin/")
    print(f"✓ Admin page: {response.status_code} (expected 302 - redirect to login)")
    assert response.status_code == 302

    # Test sitemap
    response = client.get("/sitemap.xml")
    print(f"✓ Sitemap: {response.status_code} (expected 200)")
    assert response.status_code == 200

    print("\n🎉 All basic tests passed! AI-Snakk website is working correctly.")


if __name__ == "__main__":
    test_basic_functionality()
