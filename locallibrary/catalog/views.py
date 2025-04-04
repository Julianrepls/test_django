from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Book, Author, BookInstance, Genre
from django.views import generic # esta linea se encarga de importar la clase generic de django.views





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

    # Renderiza la plantilla HTML index.html con los datos en la variable contexto
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors},
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






###################################

def author_detail(request, author_id):
    # Obtener el autor o devolver un error 404 si no existe
    author = get_object_or_404(Author, id=author_id)

    # Obtener todos los libros escritos por este autor
    books = Book.objects.filter(author=author)

    return render(request, 'catalog/author_detail.html', {'author': author, 'books': books})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'catalog/book_detail.html', {'book': book})



