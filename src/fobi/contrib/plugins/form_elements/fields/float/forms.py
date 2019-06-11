from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.widgets import NumberInput

__title__ = 'fobi.contrib.plugins.form_elements.fields.float.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('FloatInputForm',)

theme = get_theme(request=None, as_instance=True)


class FloatInputForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``FloatInputPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", "name"),
        ("help_text", ""),
        ("initial", ""),
        ("min_value", None),
        ("max_value", None),
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
    help_text = forms.CharField(
        label=_("Help text"),
        required=False,
        widget=forms.widgets.Textarea(
            attrs={'class': theme.form_element_html_class}
        ),
        help_text="This text will show up under the question and provide the \
                  survey taker with additional information."
    )
    initial = forms.FloatField(
        label=_("Default answer"),
        required=False,
        widget=NumberInput(attrs={'class': theme.form_element_html_class})
    )
    min_value = forms.FloatField(
        label=_("Minimum value"),
        required=False,
        widget=NumberInput(attrs={'class': theme.form_element_html_class}),
        help_text="The minimum value that can be entered for this question."
    )
    max_value = forms.FloatField(
        label=_("Maximum value"),
        required=False,
        widget=NumberInput(attrs={'class': theme.form_element_html_class}),
        help_text="The maximum value that can be entered for this question."
    )
    required = forms.BooleanField(
        label=_("Required"),
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': theme.form_element_checkbox_html_class}
        ),
        help_text="Is answering this question required to submit the survey?"
    )

    def clean(self):
        """Validating the values."""
        super(FloatInputForm, self).clean()

        max_value = self.cleaned_data['max_value']
        min_value = self.cleaned_data['min_value']
        initial = self.cleaned_data['initial']

        if (
            max_value is not None and min_value is not None and
            max_value < min_value
        ):
            self.add_error(
                'max_value',
                _("`max_value` should be > than `min_value`.")
            )

        if max_value is not None and initial and max_value < initial:
            self.add_error(
                'initial',
                _("`max_value` should be >= than `initial`.")
            )

        if min_value is not None and initial and min_value > initial:
            self.add_error(
                'min_value',
                _("`initial` should be >= than `min_value`.")
            )
