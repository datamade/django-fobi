===========
django-fobi
===========
`django-fobi` (or just `fobi`) is a customisable, modular, user- and developer-
friendly form generator/builder application for Django. With `fobi` you can
build Django forms using an intuitive GUI, save or mail posted form data or
even export forms into JSON format and import them on other instances. API
allows you to build your own form elements and form handlers (mechanisms for
handling the submitted form data). For full documentation,
`ReadTheDocs <http://django-fobi.readthedocs.org/#screenshots>`_.

Customizations
============
This fork has been customized to fit the needs of DataMade's
`Just Spaces <https://github.com/datamade/just-spaces>`_ project.

- The name field of FormElementEntry forms now generates a unique UUID,
  rather than requiring users to create a unique string for each survey question.
- Help text for FormElementEntry forms has been updated and expanded to
  fit its uses for the Just Spaces tool.
- FormEntry forms only display "name" field (may want to revisit this;
  see https://github.com/datamade/just-spaces/issues/63)
- A Collect Data handler is automatically attached to new FormEntry objects.
- User restrictions on form editing have been removed; permissions will be
  handled in the main Just Spaces repo.
