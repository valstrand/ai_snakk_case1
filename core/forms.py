from django import forms
from django.core.validators import validate_email
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ditt navn",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            }
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "din.epost@example.com",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            }
        )
    )

    subject = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Emne (valgfritt)",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            }
        ),
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Din melding...",
                "rows": 5,
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            }
        )
    )

    # Honeypot field for spam protection
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_honeypot(self):
        honeypot = self.cleaned_data.get("honeypot")
        if honeypot:
            raise forms.ValidationError("Bot detected")
        return honeypot

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            validate_email(email)
        return email


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Skriv inn din e-post",
                "class": "flex-1 px-4 py-3 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white",
            }
        )
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            validate_email(email)
        return email
