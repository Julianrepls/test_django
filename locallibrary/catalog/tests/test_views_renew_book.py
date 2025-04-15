from .forms import RenewBookForm

# python manage.py test catalog.tests.test_views_renew_book
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    Ver función para renovar una BookInstance específica por bibliotecario
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # Si se trata de una solicitud POST, procese los datos del formulario
    if request.method == 'POST':

        # Cree una instancia de formulario y complétela con datos de la solicitud (enlace):
        form = RenewBookForm(request.POST)

        # Compruebe si el formulario es válido:
        if form.is_valid():
            # procese los datos en form.cleaned_data según sea necesario (aquí solo los escribimos en el campo due_back del modelo)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirigir a una nueva URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # Si se trata de un GET (o cualquier otro método), cree el formulario predeterminado
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
