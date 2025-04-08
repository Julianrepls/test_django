from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Book, Author, BookInstance, Genre
from django.views import generic # esta linea se encarga de importar la clase generic de django.views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin





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
    paginate_by = 5 # esto nos hace la paginacion, movernos entre 1 o varias paginas..


class BookDetailView(generic.DetailView):
    model = Book # modelo que se va a utilizar para ver los detalles del libro, viene enlazaco desde catalog/urls.py/views.bookdetailview y contectado con book_detail.html


class AuthorListView(generic.ListView):
    model = Author


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



from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from .models import BookInstance

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


