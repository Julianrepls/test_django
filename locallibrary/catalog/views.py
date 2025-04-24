from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from .models import Book, Author, BookInstance, Genre
from django.views import generic, View                  # esta linea se encarga de importar la clase generic de django.views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DeleteView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


# import datetime
from datetime import datetime, timedelta, date
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import RenewBookForm, BookForm, LendBookForm
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


from django.forms import inlineformset_factory








def index(request):
    """
    Función vista para la página inicio del sitio.
    """
    # Genera contadores de algunos de los objetos principales
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Libros disponibles (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # El 'all()' esta implícito por defecto.
    # Numero de visitas a esta view, como está contado en la variable de sesión.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    # Renderiza la plantilla HTML index.html con los datos en la variable contexto
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors, 'num_visits':num_visits},
    )

  



class BookListView(generic.ListView):
    model = Book    # modelo que se va a utilizar para ver una lista de libros, viene enlazaco desde catalog/urls.py/views.booklistview y conectado con book_list.html
    paginate_by = 10 # esto nos hace la paginacion, movernos entre 1 o varias paginas..


class BookDetailView(generic.DetailView):
    model = Book # modelo que se va a utilizar para ver los detalles del libro, viene enlazaco desde catalog/urls.py/views.bookdetailview y contectado con book_detail.html


class AuthorListView(generic.ListView):
    model = Author
    template_name = 'catalog/author_list.html'
    context_object_name = 'author_list'


class AuthorDetailView(generic.DetailView):
    model = Author



def author_detail(request, author_id):
    # Obtener el autor o devolver un error 404 si no existe
    author = get_object_or_404(Author, id=author_id)

    # Obtener todos los libros escritos por este autor
    books = Book.objects.filter(author=author)

####################################
    # Obtener el número de copias para cada libro
    for book in books:
        book.num_copies = book.bookinstance_set.count()
# Pasar los libros al contexto junto con el número de copias
    return render(request, 'catalog/author_detail.html', {'author': author, 'books': books})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'catalog/book_detail.html', {'book': book})



#vista basada en clases para listar libros prestados (vamos a ver los libros que están prestados y a quién)
# Para restringir nuestra consulta a solamente los objetos BookInstance del usuario actual, vamos a reimplementar get_queryset()
# como se muestra abajo. Nótese que "o" es el código almacenado para "on loan" (en alquiler) y vamos a ordenar 
# por la fecha due_back para que los elementos más antiguos se muestren primero.
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Vista genérica basada en clases que enumera los libros prestados al usuario actual.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')




class LoanedBooksForLibrariansListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
    Vista que muestra todos los libros prestados, incluyendo el nombre del prestatario, solo visible para los bibliotecarios
    con el permiso 'can_mark_returned'.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    context_object_name = 'bookinstance_list'
    paginate_by = 10  # Paginación si tienes muchos registros

    # Establecer el permiso requerido
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        """
        Retorna todas las instancias de libros que están prestados.
        """
        return BookInstance.objects.filter(status='o').order_by('due_back')




class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = date.today() + timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})



#@permission_required('catalog.can_mark_returned', raise_exception=True)
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    # template_name = 'catalog/author_form.html'  
    success_url = '/catalog/authors/'  # Redirige a la lista de autores después de crear un nuevo autor
    permission_required = 'catalog.can_mark_returned'

#@permission_required('catalog.can_mark_returned', raise_exception=True)
class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    template_name = 'catalog/author_form.html'
    success_url = reverse_lazy('author-list-for-librarians')  # Redirige a la lista de autores después de actualizar
    permission_required = 'catalog.can_mark_returned'


#@permission_required('catalog.can_mark_returned', raise_exception=True)
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'catalog/author_confirm_delete.html'
    permission_required = 'catalog.can_mark_returned'



class AuthorListForLibrarians(PermissionRequiredMixin, ListView):
    model = Author
    template_name = 'catalog/author_list_for_librarians.html'
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 10


#------------------- VISTAS PARA CREAR LIBROS -------------------
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'  # Puedes usar una lista específica si quieres más control
    permission_required = 'catalog.can_mark_returned'
    success_url = '/catalog/books/' 








BookInstanceFormSet = inlineformset_factory(
    Book,
    BookInstance,
    fields=('imprint', 'due_back', 'status'),
    extra=3,
    can_delete=False
)


# con esta vista podemos crear un libro y varias instancias de él al mismo tiempo.
# Esto es útil si quieres añadir varias copias de un libro al mismo tiempo.
class BookCreateWithInstance(PermissionRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'catalog/book_with_instance_form.html'
    permission_required = 'catalog.can_mark_returned'
    success_url = '/catalog/books/'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['instance_formset'] = BookInstanceFormSet(self.request.POST)
        else:
            data['instance_formset'] = BookInstanceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        instance_formset = context['instance_formset']

        if instance_formset.is_valid():
            self.object = form.save()
            instances = instance_formset.save(commit=False)
            for instance in instances:
                instance.book = self.object
                instance.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Vista para mostrar la lista de libros para bibliotecarios, pretendo crearla para que solo ellos puedan eliminar

class BookListViewForLibrarians(PermissionRequiredMixin, ListView):
    model = Book
    template_name = 'catalog/book_list_for_librarians.html'  # Nueva plantilla para la vista de libros para bibliotecarios
    context_object_name = 'books'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(DeleteView):

    model = Book
    success_url = reverse_lazy('books')  # Redirige a la lista de libros después de eliminar
    template_name = 'catalog/book_confirm_delete.html'







#--------------- VISTA PARA PRESTAR LIBROS ------------------        
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class AvailableBooksView(ListView):
    model = BookInstance
    template_name = 'catalog/available_books.html'
    context_object_name = 'book_instances'

    def get_queryset(self):
        return BookInstance.objects.filter(status='a')
    


@permission_required('catalog.can_mark_returned')
def lend_book_librarian(request, pk):
    """
    View function for lending a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # Check if the book is available
    if book_inst.status != 'a':
        return render(request, 'catalog/book_lend_librarian.html', {
            'form': None,
            'bookinst': book_inst,
            'error': 'Este libro no está disponible para prestar.'
        })

    # If this is a POST request, process the form data
    if request.method == 'POST':
        form = LendBookForm(request.POST)
        if form.is_valid():
            book_inst.borrower = form.cleaned_data['borrower']
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.status = 'o'  # Set status to "On loan"
            book_inst.save()
            return HttpResponseRedirect(reverse('available-books'))
    else:
        proposed_due_back = datetime.today().date() + timedelta(weeks=3)
        form = LendBookForm(initial={'due_back': proposed_due_back})

    return render(request, 'catalog/book_lend_librarian.html', {
        'form': form,
        'bookinst': book_inst
    })


# ------------------- VISTA PARA MARCAR LIBRO DEVUELTO -------------------
@permission_required('catalog.can_mark_returned')
def mark_book_returned(request, pk):
    """
    View function for marking a specific BookInstance as returned
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        # Cambiar el estado del libro a "Available"
        book_inst.status = 'a'
        book_inst.borrower = None
        book_inst.due_back = None
        book_inst.save()

        return HttpResponseRedirect(reverse('all-borrowed'))

    return render(request, 'catalog/book_confirm_return.html', {'bookinst': book_inst})