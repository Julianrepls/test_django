from django import forms
from .models import Book, User


from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import datetime #para comprobar la fecha de hoy en el renovar libro
from datetime import datetime

# -------------- formulario para renovar libros --------------
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


#--------- En este formulario se puede crear libro y copias -------------
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre']
        widgets = {
            'genre': forms.CheckboxSelectMultiple(),  # Muestra los géneros como casillas
        }


#--------- En este formulario se puede seleccionar el libro y el prestatario y la fecha de devolución. -------------
class LendBookForm(forms.Form):
    borrower = forms.ModelChoiceField(
        queryset=User.objects.all(),  # Cambiado para incluir a todos los usuarios
        label="Prestatario",
        help_text="Seleccione un usuario"
    )
    due_back = forms.DateField(
        label="Fecha de devolución",
        help_text="Fecha en que el libro debe ser devuelto"
    )

    def clean_due_back(self):
        date = self.cleaned_data['due_back']
        if date < datetime.today().date():
            raise ValidationError("La fecha de devolución no puede ser en el pasado.")
        return date