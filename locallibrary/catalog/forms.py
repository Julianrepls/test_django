from django import forms
from .models import Book, BookInstance
from django.forms import modelformset_factory

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import datetime #for checking renewal date range.

# formulario para renovar libros:
class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        #widget=forms.TextInput(attrs={'type': 'date'}),     # si qito este comentario con este comando no me deja poner la fecha en el formulario pero en su lugar me pone un calendario.
        help_text="Enter a date between now and 4 weeks (default 3)."
        )

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        #Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data



class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre']
        widgets = {
            'genre': forms.CheckboxSelectMultiple(),  # Muestra los géneros como casillas
        }

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['imprint']

