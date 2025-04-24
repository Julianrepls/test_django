from django import forms
from .models import Book, User


from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
#import datetime #para comprobar la fecha de hoy en el renovar libro
from datetime import date, timedelta

# -------------- formulario para renovar libros --------------
class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Introduce una fecha entre hoy y 4 semanas (por defecto es 3 semanas).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        # Verifica que la fecha no esté en el pasado
        if data < date.today():
            raise forms.ValidationError("La fecha no puede estar en el pasado.")

        # Verifica que no pase de 4 semanas en el futuro
        if data > date.today() + timedelta(weeks=4):
            raise forms.ValidationError("La fecha no puede estar más allá de 4 semanas en el futuro.")

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
        if date < date.today():
            raise ValidationError("La fecha de devolución no puede ser en el pasado.")
        return date