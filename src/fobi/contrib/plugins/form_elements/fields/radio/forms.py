from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.helpers import validate_initial_for_choices

__title__ = 'fobi.contrib.plugins.form_elements.fields.select.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('RadioInputForm',)

theme = get_theme(request=None, as_instance=True)


class RadioInputForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``RadioInputPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", "name"),
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
        widget=forms.widgets.HiddenInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    choices = forms.CharField(
        label=_("Choices"),
        required=True,
        help_text=_("Enter a single choice option per line. Example:<br/>"
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
        )
    )
    initial = forms.CharField(
        label=_("Initial value"),
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
        #
        # availalble_choices = dict(
        #     get_select_field_choices(self.cleaned_data['choices'])
        #     ).values()
        #
        # if not self.cleaned_data['initial'] in availalble_choices:
        #     raise forms.ValidationError(
        #         _("Invalid value for initial! Should be any of the "
        #           "following: {0}".format(','.join(availalble_choices)))
        #         )
        # return self.cleaned_data['initial']
