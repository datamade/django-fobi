"""
Class based views.
"""
import datetime
import logging

from collections import OrderedDict

import simplejson as json

# from six import string_types

from django.db import models, IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic import View, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin


from nine import versions

from ..base import (
    # fire_form_callbacks,
    # run_form_handlers,
    # run_form_wizard_handlers,
    # form_element_plugin_registry,
    # form_handler_plugin_registry,
    # form_wizard_handler_plugin_registry,
    # submit_plugin_form_data,
    get_theme,    
)
from ..constants import (
    CALLBACK_BEFORE_FORM_VALIDATION,
    CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA,
    CALLBACK_FORM_VALID,
    CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS,
    CALLBACK_FORM_INVALID,
)
from ..decorators import permissions_required, SATISFY_ALL, SATISFY_ANY
from ..dynamic import assemble_form_class
from ..form_importers import (
    ensure_autodiscover as ensure_importers_autodiscover,
    form_importer_plugin_registry, get_form_importer_plugin_urls,
)
from ..forms import (
    # FormEntryForm,
    # FormElementEntryFormSet,
    # ImportFormEntryForm,
    # ImportFormWizardEntryForm,
    FormWizardEntryForm,
    # FormWizardFormEntry,
    FormWizardFormEntryFormSet,
    # FormWizardFormEntryForm,
)
from ..helpers import JSONDataExporter
from ..models import (
    FormEntry,
    # FormElementEntry,
    # FormHandlerEntry,
    FormWizardEntry,
    # FormWizardFormEntry,
    # FormWizardHandlerEntry,
)
from ..settings import (
    GET_PARAM_INITIAL_DATA,
    DEBUG,
    SORT_PLUGINS_BY_VALUE,
)
from ..utils import (
    # append_edit_and_delete_links_to_field,
    # get_user_form_element_plugins_grouped,
    # get_user_form_field_plugin_uids,
    # get_user_form_element_plugins,
    # get_user_form_handler_plugins_grouped,
    # get_user_form_handler_plugins,
    get_user_form_wizard_handler_plugins,
    # get_user_form_handler_plugin_uids,
    # get_user_form_wizard_handler_plugin_uids,
    # get_wizard_files_upload_dir,
    # perform_form_entry_import,
    # prepare_form_entry_export_data,
)
from ..wizard import (
    # DynamicCookieWizardView,
    DynamicSessionWizardView,
)

if versions.DJANGO_GTE_1_10:
    from django.shortcuts import render, redirect
    from django.urls import reverse, reverse_lazy
else:
    from django.core.urlresolvers import reverse, reverse_lazy
    from django.shortcuts import render_to_response, redirect
    from django.template import RequestContext

if versions.DJANGO_GTE_1_8:
    from formtools.wizard.forms import ManagementForm
else:
    from django.contrib.formtools.wizard.forms import ManagementForm

__title__ = 'fobi.views.class_based'
__author__ = 'Kyle Roux <jstacoder@gmail.com>'
__copyright__ = '2018 Kyle Roux'
__license__ = 'GPL 2.0/LGPL 2.1'


__all__ = (
    'FormWizardView', 
    'FobiThemeMixin',
    'FobiFormRedirectMixin',
    'CreateFormWizardEntryView',
    'EditFormWizardEntryView',
)


# *****************************************************************************
# ************************ View form wizard entry *****************************
# *****************************************************************************


class FormWizardView(DynamicSessionWizardView):
    """Dynamic form wizard."""

    file_storage = FileSystemStorage(
        location=get_wizard_files_upload_dir()
    )

    def get_context_data(self, form, **kwargs):
        """Get context data."""
        context_data = super(FormWizardView, self).get_context_data(
            form=form, **kwargs
        )
        form_entry = self.get_form_entry_for_step(self.steps.step0)
        context_data.update({
            'form_wizard_entry': self.form_wizard_entry,
            'form_wizard_mode': True,
            'fobi_theme': self.fobi_theme,
            'fobi_form_title': form_entry.title,
            'fobi_form_wizard_title': self.form_wizard_entry.title,
            'steps_range': range(1, self.steps.count + 1),
        })

        return context_data

    def get_form_entry_for_step(self, step):
        """Get form entry title for step."""
        form_slug = self.form_list[self.steps.step0][0]
        return self.form_entry_mapping[form_slug]

    def get_initial_wizard_data(self, request, *args, **kwargs):
        """Get initial wizard data."""
        if versions.DJANGO_GTE_1_10:
            user_is_authenticated = request.user.is_authenticated
        else:
            user_is_authenticated = request.user.is_authenticated()
        try:
            qs_kwargs = {'slug': kwargs.get('form_wizard_entry_slug')}
            if not user_is_authenticated:
                qs_kwargs.update({'is_public': True})
            form_wizard_entry = FormWizardEntry.objects \
                .select_related('user') \
                .get(**qs_kwargs)
        except ObjectDoesNotExist as err:
            raise Http404(ugettext("Form wizard entry not found."))

        form_entries = [
            form_wizard_form_entry.form_entry
            for form_wizard_form_entry
            in form_wizard_entry.formwizardformentry_set
                                .all()
                                .select_related('form_entry')
        ]
        form_list = []
        form_entry_mapping = {}
        form_element_entry_mapping = {}
        wizard_form_element_entries = []
        for creation_counter, form_entry in enumerate(form_entries):
            # Using frozen queryset to minimize query usage
            form_element_entries = form_entry.formelemententry_set.all()[:]
            wizard_form_element_entries += form_element_entries
            form_cls = assemble_form_class(
                form_entry,
                request=request,
                form_element_entries=form_element_entries,
                get_form_field_instances_kwargs={
                    'form_wizard_entry': form_wizard_entry,
                }
            )

            form_list.append(
                (form_entry.slug, form_cls)
            )
            form_entry_mapping[form_entry.slug] = form_entry
            form_element_entry_mapping[form_entry.slug] = form_element_entries

        if len(form_list) == 0:
            raise Http404(
                ugettext("Form wizard entry does not contain any forms.")
            )

        theme = get_theme(request=request, as_instance=True)
        theme.collect_plugin_media(wizard_form_element_entries)

        return {
            'form_list': form_list,
            'template_name': theme.view_form_wizard_entry_template,
            'form_wizard_entry': form_wizard_entry,
            'wizard_form_element_entries': wizard_form_element_entries,
            'form_entry_mapping': form_entry_mapping,
            'form_element_entry_mapping': form_element_entry_mapping,
            'fobi_theme': theme,
        }

    def post(self, *args, **kwargs):
        """POST requests.

        This method handles POST requests.

        The wizard will render either the current step (if form validation
        wasn't successful), the next step (if the current step was stored
        successful) or the done view (if no more steps are available)
        """
        # Without this fix POST actions breaks on Django 1.11. Introduce
        # a better fix if you can.
        if versions.DJANGO_GTE_1_11:
            self.request.POST._mutable = True

        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)

        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                _('ManagementForm data is missing or has been tampered.'),
                code='missing_management_form',
            )

        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step

        # get the form for the current step
        form = self.get_form(data=self.request.POST, files=self.request.FILES)

        # and try to validate
        if form.is_valid():
            # Get current form entry
            form_entry = self.form_entry_mapping[self.steps.current]
            # Get form elements for the current form entry
            form_element_entries = \
                self.form_element_entry_mapping[self.steps.current]
            # Fire plugin processors
            form = submit_plugin_form_data(
                form_entry=form_entry,
                request=self.request,
                form=form,
                form_element_entries=form_element_entries,
                **{'form_wizard_entry': self.form_wizard_entry}
            )
            # Form wizards make use of form.data instead of form.cleaned_data.
            # Therefore, we update the form.data with values from
            # form.cleaned_data.
            wizard_field_pattern = "{0}-{1}"
            # We can't update values of a `MultiValueDict`, which `QueryDict`
            # is, using `update` method. That's why we do it one by one.
            for field_key, field_value in form.cleaned_data.items():
                wizard_form_key = wizard_field_pattern.format(
                    self.steps.current,
                    field_key
                )
                # Do not overwrite field data. Only empty or missing values.
                if not (
                    wizard_form_key in form.data
                    and form.data[wizard_form_key]
                ):
                    form.data[wizard_form_key] = field_value

                # This is dirty hack to make wizard validate empty multiple
                # choice fields. Otherwise it would fail with message
                # Select a valid choice. [] is not one of the available
                # choices.
                if wizard_form_key in form.data:
                    if not form.data[wizard_form_key]:
                        if isinstance(form.data[wizard_form_key], list):
                            del form.data[wizard_form_key]

            # if the form is valid, store the cleaned data and files.
            self.storage.set_step_data(self.steps.current,
                                       self.process_step(form))

            self.storage.set_step_files(self.steps.current,
                                        self.process_step_files(form))

            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form)
        return self.render(form)

    def get_ignorable_field_names(self, form_element_entries):
        """Get ignorable field names."""
        ignorable_field_names = []
        for form_element_entry in form_element_entries:
            plugin = form_element_entry.get_plugin()
            # If plugin doesn't have a value, we don't need to have it
            # on the last step (otherwise validation issues may arise, as
            # it happens with captcha/re-captcha).
            if not plugin.has_value:
                ignorable_field_names.append(plugin.data.name)
        return ignorable_field_names

    def render_done(self, form, **kwargs):
        """Render done.

        This method gets called when all forms passed. The method should also
        re-validate all steps to prevent manipulation. If any form fails to
        validate, `render_revalidation_failure` should get called.
        If everything is fine call `done`.
        """
        final_forms = OrderedDict()
        # walk through the form list and try to validate the data again.
        for form_key in self.get_form_list():

            form_obj = self.get_form(
                step=form_key,
                data=self.storage.get_step_data(form_key),
                files=self.storage.get_step_files(form_key)
            )

            # Get form elements for the current form entry
            form_element_entries = \
                self.form_element_entry_mapping[form_key]

            ignorable_field_names = self.get_ignorable_field_names(
                form_element_entries
            )

            for ignorable_field_name in ignorable_field_names:
                if ignorable_field_name in form_obj.fields:
                    form_obj.fields.pop(ignorable_field_name)

            if not form_obj.is_valid():
                return self.render_revalidation_failure(form_key,
                                                        form_obj,
                                                        **kwargs)

            # Fire plugin processors
            # Get current form entry
            form_entry = self.form_entry_mapping[form_key]

            form_obj = submit_plugin_form_data(
                form_entry=form_entry,
                request=self.request,
                form=form_obj,
                form_element_entries=form_element_entries,
                **{'form_wizard_entry': self.form_wizard_entry}
            )

            final_forms[form_key] = form_obj

        # render the done view and reset the wizard before returning the
        # response. This is needed to prevent from rendering done with the
        # same data twice.
        done_response = self.done(final_forms.values(),
                                  form_dict=final_forms,
                                  **kwargs)
        self.storage.reset()
        return done_response

    def done(self, form_list, **kwargs):
        """Done."""
        if versions.DJANGO_GTE_1_10:
            user_is_authenticated = self.request.user.is_authenticated
        else:
            user_is_authenticated = self.request.user.is_authenticated()
        try:
            qs_kwargs = {'slug': kwargs.get('form_wizard_entry_slug')}
            if not user_is_authenticated:
                kwargs.update({'is_public': True})
            form_wizard_entry = FormWizardEntry.objects \
                .select_related('user') \
                .get(**qs_kwargs)
        except ObjectDoesNotExist as err:
            raise Http404(ugettext("Form wizard entry not found."))

        # Run all handlers
        handler_responses, handler_errors = run_form_wizard_handlers(
            form_wizard_entry=form_wizard_entry,
            request=self.request,
            form_list=form_list,
            form_wizard=self,
            form_element_entries=self.wizard_form_element_entries
        )

        # do_something_with_the_form_data(form_list)
        redirect_url = reverse('fobi.form_wizard_entry_submitted',
                               args=[form_wizard_entry.slug])
        return HttpResponseRedirect(redirect_url)

class FobiThemeMixin(TemplateView):
    theme = None
    template_name = None
    theme_template_name = None

    def get_theme_template_name(self):
        return self.theme_template_name

    def get_theme(self, request, theme=None):
        if theme is None:
            theme = get_theme(request=request, as_instance=True)
        self.theme = theme
        return self.theme

    def get_template_names(self):
        if self.template_name is None:
            self.template_name = getattr(
                self.theme, self.get_theme_template_name())
        return [self.template_name]

class FobiFormRedirectMixin(FormMixin):
    object = None
    form_valid_redirect = None
    form_valid_redirect_kwargs = None
    success_message = None
    error_message = None

    def get_success_message(self):
        return self.success_message

    def get_error_message(self, e):
        return self.error_message

    def get_form_valid_redirect(self, *args, **kwargs):
        return self.form_valid_redirect

    def _get_form_valid_redirect_kwargs(self, *args, **kwargs):
        return self.form_valid_redirect_kwargs

    def get_form_valid_redirect_kwargs(self, result=None,  *args, **kwargs):
        form_valid_redirect_kwargs = dict()
        for key, value_key in self._get_form_valid_redirect_kwargs():
            form_valid_redirect_kwargs.update(
                {
                    key: getattr(
                        result,
                        value_key
                    )
                }
            )
        return form_valid_redirect_kwargs

    def get_success_url(self, *args, **kwargs):
        reverse_kwargs = self.get_form_valid_redirect_kwargs(
            result=self.object)
        return reverse_lazy(
            self.get_form_valid_redirect(),
            kwargs=reverse_kwargs
        )

    def form_valid(self, form=None):
        if form is None:
            form = self.get_form()
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        try:
            self.object.save()
            messages.info(
                self.request,
                ugettext(
                    self.get_success_message()
                )
            )
            return redirect(self.get_success_url())
        except IntegrityError as e:
            messages.info(
                self.request,
                ugettext(
                    self.get_error_message(e)
                )
            )
            return super(FobiFormRedirectMixin, self).form_invalid(form)

class CreateFormWizardEntryView(FobiThemeMixin, FobiFormRedirectMixin, SingleObjectMixin):
    result = None
    model = FormWizardEntry
    form_class = FormWizardEntryForm
    context_object_name = 'form_wizard_entry'
    theme_template_name = 'create_form_wizard_entry_template'
    form_valid_redirect = 'fobi_edit_wizard'
    form_valid_redirect_kwargs = (
        ('form_wizard_entry_id', 'pk'),
    )

    def get_success_message(self):
        return 'Form wizard {0} was created successfully.'.format(self.object.name)

    def get_error_message(self, e):
        return 'Errors occurred while saving the form wizard: {0}.'.format(str(e))

    def dispatch(self, request, theme=None, *args, **kwargs):
        self.get_theme(request)
        return super(CreateFormWizardEntryView, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        return super(CreateFormWizardEntryView, self).form_valid()

    def get_context_data(self, **kwargs):
        context = super(CreateFormWizardEntryView,
                        self).get_context_data(**kwargs)
        if self.theme:
            context['fobi_theme'] = self.theme
        return context

    def get_form(self, form_class=None):
        form_args = [] if self.request.method == 'GET' else [
            self.request.POST, self.request.FILES]
        form_kwargs = dict(request=self.request)
        if form_class is None:
            form_class = self.form_class
        return form_class(*form_args, **form_kwargs)

class EditFormWizardEntryView(FobiFormRedirectMixin, FobiThemeMixin, SingleObjectMixin):
    form_wizard_entry_id = None
    theme = None
    model = FormWizardEntry
    pk_url_kwarg = 'form_wizard_entry_id'
    form_class = FormWizardEntryForm
    _form_wizard_form_entry_formset = None
    form_valid_redirect = 'fobi.edit_form_wizard_entry'
    form_valid_redirect_kwargs = (
        ('form_wizard_entry_id', 'pk')
    )
    context_object_name = 'form_wizard_entry'
    theme_template_name = 'edit_form_wizard_entry_template'

    def get_success_message(self):
        return "Form wizard {0} was edited successfully".format(self.object.name)

    def get_error_message(self, e):
        return "Errors occurred while saving the Form wizard {0}".format(e)

    def get_context_data(self, **kwargs):
        context = super(EditFormWizardEntryView,
                        self).get_context_data(**kwargs)
        context['form_wizard_entry_forms'] = self.object.formwizardformentry_set \
            .all().select_related('form_entry') \
            .order_by('position')[:]

        context['form_wizard_handlers'] = self.object.formwizardhandlerentry_set.all()[:]
        context['used_form_wizard_handler_uids'] = [
            form_wizard_handler.plugin_uid
            for form_wizard_handler
            in context['form_wizard_handlers']
        ]
        context['form_wizard_form_entry_ids'] = [
            _f.form_entry_id
            for _f in context['form_wizard_handlers']
        ]
        context['all_form_entries'] = FormEntry._default_manager \
                                               .only('id', 'name', 'slug') \
                                               .filter(user__pk=self.request.user.pk) \
                                               .exclude(id__in=context['form_wizard_form_entry_ids'])

        context['user_form_wizard_handler_plugins'] = get_user_form_wizard_handler_plugins(
            self.request.user,
            exclude_used_singles=True,
            used_form_wizard_handler_plugin_uids=context['used_form_wizard_handler_uids'],
        )

        theme = self.get_theme(request=self.request)
        context['form_wizard_form_entry_formset'] = self.form_wizard_form_entry_formset

        context['fobi_theme'] = theme
        return context

    def dispatch(self, request, *args, **kwargs):
        self.form_wizard_entry_id = kwargs.pop('form_wizard_entry_id', None)
        self.object = self.get_object()
        return super(EditFormWizardEntryView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model._default_manager \
                         .select_related('user') \
                         .prefetch_related('formwizardformentry_set')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(pk=self.form_wizard_entry_id, user__pk=self.request.user.pk)
        except self.model.ObjectDoesNotExist as err:
            raise Http404(ugettext('not found'))

    def get_form_kwargs(self):
        kwargs = super(EditFormWizardEntryView, self).get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        if 'request' not in kwargs:
            kwargs.update({'request': self.request})
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.form_class
        form_args = []
        if self.request.method == 'POST':
            form_args = [self.request.POST, self.request.FILES]
        return form_class(*form_args, **self.get_form_kwargs())

    @property
    def form_wizard_form_entry_formset(self):
        if self._form_wizard_form_entry_formset is None:
            return FormWizardFormEntryFormSet(
                queryset=self.object.formwizardformentry_set.all()
            )
        return self._form_wizard_form_entry_formset

    @form_wizard_form_entry_formset.setter
    def form_wizard_form_entry_formset(self, value):
        self._form_wizard_form_entry_formset = value

    def post(self, *args, **kwargs):
        if 'ordering' in self.request.POST:
            self.form_wizard_form_entry_formset = FormWizardFormEntryFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=self.object.formwizardformentry_set.all(),
                # prefix = 'form_element'
            )
            try:
                if self.form_wizard_form_entry_formset.is_valid():
                    self.form_wizard_form_entry_formset.save()
                    messages.info(
                        self.request,
                        _("Forms ordering edited successfully.")
                    )
                    return redirect(
                        self.get_success_url()
                    )
            except MultiValueDictKeyError as err:
                messages.error(
                    self.request,
                    _("Errors occurred while trying to change the "
                      "elements ordering!")
                )
                return redirect(
                    self.get_success_url()
                )
        form = self.get_form()(self.get_form_kwargs())
        if form.is_valid():
            return super(EditFormWizardEntryView, self).form_valid(form=form)
        return super(EditFormWizardEntryView, self).form_invalid(form=form)
