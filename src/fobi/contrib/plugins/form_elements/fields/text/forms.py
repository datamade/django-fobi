from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.settings import DEFAULT_MAX_LENGTH, DEFAULT_MIN_LENGTH
from fobi.widgets import NumberInput

__title__ = 'fobi.contrib.plugins.form_elements.fields.text.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('TextInputForm',)

theme = get_theme(request=None, as_instance=True)


class TextInputForm(forms.Form, BaseFormFieldPluginForm):
    """Form for ``TextInputPlugin``."""

    plugin_data_fields = [
        ("label", ""),
        ("name", "name"),
        ("help_text", ""),
        ("initial", ""),
        ("max_length", str(DEFAULT_MAX_LENGTH)),
        ("required", False),
        ("placeholder", ""),
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
        widget=forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    max_length = forms.IntegerField(
        label=_("Max length"),
        required=True,
        widget=NumberInput(attrs={'class': theme.form_element_html_class,
                                  'min': str(DEFAULT_MIN_LENGTH)}),
        initial=DEFAULT_MAX_LENGTH,
        validators=[MinValueValidator(DEFAULT_MIN_LENGTH)],
        help_text="The maximum number of characters that can be submitted for \
                  this question."
    )
    required = forms.BooleanField(
        label=_("Required"),
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': theme.form_element_checkbox_html_class}
        ),
        help_text="Is answering this question required to submit the survey?"
    )
    placeholder = forms.CharField(
        label=_("Placeholder"),
        required=False,
        widget=forms.widgets.HiddenInput(
            attrs={'class': theme.form_element_html_class}
        )
    )

    def clean(self):
        """Validation."""
        super(TextInputForm, self).clean()

        max_length = self.cleaned_data.get('max_length', DEFAULT_MAX_LENGTH)

        if self.cleaned_data['initial']:
            len_initial = len(self.cleaned_data['initial'])
            if len_initial > max_length:
                self.add_error(
                    'initial',
                    _("Ensure this value has at most {0} characters "
                      "(it has {1}).".format(max_length, len_initial))
                )
