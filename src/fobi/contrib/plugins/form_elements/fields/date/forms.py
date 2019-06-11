from __future__ import absolute_import

from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BaseFormFieldPluginForm, get_theme

__title__ = 'fobi.contrib.plugins.form_elements.fields.date.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DateInputForm',)


theme = get_theme(request=None, as_instance=True)


class DateInputForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``DateInputPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", "name"),
        ("help_text", ""),
        ("initial", ""),
        ("required", False),
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
    initial = forms.DateField(
        label=_("Default answer"),
        required=False,
        widget=forms.widgets.DateInput(
            attrs={'class': theme.form_element_html_class, 'type': 'date'}
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

    def clean_initial(self):
        """Clean the initial value."""
        initial = self.cleaned_data['initial']
        try:
            return initial.strftime("%Y-%m-%d")
        except Exception as err:
            return initial
