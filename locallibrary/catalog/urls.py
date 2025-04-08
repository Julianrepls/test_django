from django.urls import path
from . import views
from .views import author_detail #recuerda esto lo hacemos para poder usar la vista author_detail que hemos creado en views.py
from .views import book_detail # recuerda esto lo hacemos para poder usar la vista book_detail que hemos creado en views.py




#estos son nuestros mapeadores de URL
urlpatterns = [
    path('', views.index, name='index'),                                # esta línea se encarga de mostrar la página de inicio
    path('books/', views.BookListView.as_view(), name='books'),         #esta línea se encarga de mostrar la lista de libros
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),  #esta línea se encarga de mostrar los detalles de un libro. Esto está enlazado a la vista BookDetailView en views.py con el html de book_list.html
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),  
    path('author/<int:author_id>/', author_detail, name='author-detail'),
    path('book/<int:book_id>/', book_detail, name='book-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'), #Configuración URL para libros alquilados
    path('allborrowed/', views.LoanedBooksForLibrariansListView.as_view(), name='all-borrowed'),
    path('borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),


    #path('myurl/<fish>', views.my_view, {'my_template_name': 'some_path'}, name='aurl'), # esta línea se encarga de mostrar una vista personalizada con un template específico. Esto está enlazado a la vista my_view en views.py con el html de book_list.html


]