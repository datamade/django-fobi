from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.helpers import validate_initial_for_multiple_choices

import uuid

__title__ = 'fobi.contrib.plugins.form_elements.fields.' \
            'checkbox_select_multiple.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('CheckboxSelectMultipleInputForm',)

theme = get_theme(request=None, as_instance=True)


class CheckboxSelectMultipleInputForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``CheckboxSelectMultipleInputPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", "name"),
        ("choices", ""),
        ("help_text", ""),
        ("initial", ""),
        ("required", False)
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
    choices = forms.CharField(
        label=_("Choices"),
        required=True,
        help_text=_("Enter a single choice option per line. For example:<br/>"
                    "<code>Not at all familiar</code><br/>"
                    "<code>Slightly familiar</code><br/>"
                    "<code>Somewhat familiar</code><br/>"
                    "<code>Moderately familiar</code><br/>"
                    "<code>Extremely familiar</code>"
                    ),
        widget=forms.widgets.Textarea(
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
    required = forms.BooleanField(
        label=_("Required"),
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': theme.form_element_checkbox_html_class}
        ),
        help_text="Is answering this question required to submit the survey?"
    )

    def clean_initial(self):
        """Validating the initial value."""
        return validate_initial_for_multiple_choices(self,
                                                     'choices',
                                                     'initial')
