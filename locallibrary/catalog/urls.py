from django.urls import path
from . import views
from .views import author_detail #recuerda esto lo hacemos para poder usar la vista author_detail que hemos creado en views.py
from .views import book_detail # recuerda esto lo hacemos para poder usar la vista book_detail que hemos creado en views.py
from .views import AuthorDelete, AuthorListView, AuthorUpdate, AuthorListForLibrarians, BookCreate, BookCreateWithInstance, BookDelete


#estos son nuestros mapeadores de URL
urlpatterns = [
    path('', views.index, name='index'),                                # esta línea se encarga de mostrar la página de inicio
    path('books/', views.BookListView.as_view(), name='books'),         #esta línea se encarga de mostrar la lista de libros
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),  #esta línea se encarga de mostrar los detalles de un libro. Esto está enlazado a la vista BookDetailView en views.py con el html de book_list.html
    path('authors/', views.AuthorListView.as_view(), name='authors'),
     
    path('author/<int:author_id>/', author_detail, name='author-detail'),
    path('book/<int:book_id>/', book_detail, name='book-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),                #Configuración URL para libros alquilados por el usuario
    path('allborrowed/', views.LoanedBooksForLibrariansListView.as_view(), name='all-borrowed'),    #Configuración URL para libros alquilados para bibliotecarios 
    path('borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),                 #Configuración URL para libros alquilados para todos los usuarios
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),         #esta línea se encarga de mostrar la vista de renovación de libros. Esto está enlazado a la vista renew_book_librarian en views.py con el html de book_list.html
    
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),
    path('author/<int:pk>/update/', AuthorUpdate.as_view(), name='author-update'),
    path('authors/librarians/', AuthorListForLibrarians.as_view(), name='author-list-librarians'),
    path('authors/librarians/', views.AuthorListForLibrarians.as_view(), name='author-list-for-librarians'),
    
    path('authors/', AuthorListView.as_view(), name='author-list'),   # esta línea se encarga de mostrar la lista de autores. Esto está enlazado a la vista AuthorListView en views.py con el html de author_list.html
    
    path('book/create/', BookCreate.as_view(), name='book-create'),
    path('book/create_with_instance/', BookCreateWithInstance.as_view(), name='book-create-with-instance'),
    path('book/create/', views.BookCreateWithInstance.as_view(), name='book-create'),
    path('books/librarians/', views.BookListViewForLibrarians.as_view(), name='book-list-for-librarians'),
    path('book/<int:pk>/delete/', BookDelete.as_view(), name='book-delete'),



    
    


    #path('myurl/<fish>', views.my_view, {'my_template_name': 'some_path'}, name='aurl'), # esta línea se encarga de mostrar una vista personalizada con un template específico. Esto está enlazado a la vista my_view en views.py con el html de book_list.html


]