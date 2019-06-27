from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.widgets import NumberInput

__title__ = 'fobi.contrib.plugins.form_elements.fields.textarea.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('TextareaForm',)

theme = get_theme(request=None, as_instance=True)


class TextareaForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``TextareaPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", "name"),
        ("help_text", ""),
        ("initial", ""),
        ("required", False),
        ("max_length", ""),
        ("placeholder", "")
    ]

    label = forms.CharField(
        label=_("Question text"),
        required=True,
        widget=forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    name = forms.CharField(
        label=_("Name"),
        required=True,
        widget=forms.widgets.HiddenInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    help_text = forms.CharField(
        label=_("Help text"),
        required=False,
        widget=forms.widgets.Textarea(
            attrs={'class': theme.form_element_html_class}
        ),
        help_text="This text will show up under the question and provide the \
                  survey taker with additional information."
    )
    initial = forms.CharField(
        label=_("Default answer"),
        required=False,
        widget=forms.widgets.Textarea(
            attrs={'class': theme.form_element_html_class}
        )
    )
    required = forms.BooleanField(
        label=_("Required"),
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': theme.form_element_checkbox_html_class}
        ),
        help_text="Is answering this question required to submit the survey?"
    )
    max_length = forms.IntegerField(
        label=_("Maximum length"),
        required=False,
        widget=NumberInput(
            attrs={'class': theme.form_element_html_class}
        ),
        help_text="The maximum number of characters that can be submitted for \
                  this question."
    )
    placeholder = forms.CharField(
        label=_("Placeholder"),
        required=False,
        widget=forms.widgets.HiddenInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
