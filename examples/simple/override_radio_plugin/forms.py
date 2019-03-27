from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.helpers import validate_initial_for_choices

theme = get_theme(request=None, as_instance=True)

__all__ = ('RadioInputForm',)


class RadioInputForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``RadioInputPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", ""),
        ("choices", ""),
        ("help_text", ""),
        ("initial", ""),
        ("required", False)
    ]

    label = forms.CharField(
        label=_("Label"),
        required=True,
        widget=forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    name = forms.CharField(
        label=_("Name"),
        required=True,
        widget=forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    choices = forms.CharField(
        label=_("Choices"),
        required=False,
        help_text=_("Enter single choice option per line. Example:<br/>"
                    "<code>Not at all familiar<br/>"
                    "Slightly familiar<br/>"
                    "Somewhat familiar<br/>"
                    "Moderately familiar<br/>"
                    "Extremely familiar<br/></code>"
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
        )
    )
    initial = forms.CharField(
        label=_("Initial"),
        required=False,
        widget=forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    required = forms.BooleanField(
        label=_("Required"),
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': theme.form_element_checkbox_html_class}
        )
    )

    def clean_initial(self):
        """Validating the initial value."""
        return validate_initial_for_choices(self, 'choices', 'initial')
