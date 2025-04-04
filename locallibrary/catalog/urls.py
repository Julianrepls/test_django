from django.urls import path
from . import views

#estos son nuestros mapeadores de URL
urlpatterns = [
    path('', views.index, name='index'),                                # esta línea se encarga de mostrar la página de inicio
    path('books/', views.BookListView.as_view(), name='books'),         #esta línea se encarga de mostrar la lista de libros
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),  #esta línea se encarga de mostrar los detalles de un libro. Esto está enlazado a la vista BookDetailView en views.py con el html de book_list.html
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),  
     
              
    #path('myurl/<fish>', views.my_view, {'my_template_name': 'some_path'}, name='aurl'), # esta línea se encarga de mostrar una vista personalizada con un template específico. Esto está enlazado a la vista my_view en views.py con el html de book_list.html


]