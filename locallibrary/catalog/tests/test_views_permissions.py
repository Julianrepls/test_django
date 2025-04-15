# Esto crea dos usuarios y dos instancias de libros, pero solo otorga a un usuario el permiso necesario para acceder a la vista
# python manage.py test catalog.tests.test_views_permissions

from django.contrib.auth.models import Permission # Requerido para otorgar el permiso necesario para establecer un libro como devuelto.
from django.test import TestCase
from django.urls import reverse
import datetime

from django.contrib.auth import get_user_model
User = get_user_model()

from ..models import Book, Author, BookInstance, Genre



class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        #Crear un usuario
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        #Crear un libro
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author)
        # Crear género como un paso posterior
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # No se permite la asignación directa de tipos de muchos a muchos.
        test_book.save()

        #Cree un objeto BookInstance para test_user1
        return_date= datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user1, status='o')

        #Cree un objeto BookInstance para test_user2
        return_date= datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user2, status='o')


    """
    Agregamos las siguientes pruebas al final de la clase de prueba. Estos comprueban que solo los usuarios 
    con los permisos correctos (testuser2) pueden acceder a la vista. Verificamos todos los casos: cuando 
    el usuario no ha iniciado sesión, cuando un usuario ha iniciado sesión pero no tiene los permisos correctos, 
    cuando el usuario tiene permisos pero no es el prestatario (debería tener éxito) y qué sucede cuando intenta 
    acceder a una BookInstance que no existe. También comprobamos que se utiliza la plantilla correcta.
    """

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        #Revisar manualmente la redirección (no se puede usar assertRedirect, porque la URL de redirección es impredecible)
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )

        #Revisar manualmente la redirección (no se puede usar assertRedirect, porque la URL de redirección es impredecible)
        self.assertEqual( resp.status_code,302)
        self.assertTrue( resp.url.startswith('/accounts/login/') )

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk,}) )

        #Comprobar que nos permita iniciar sesión: este es nuestro libro y tenemos los permisos correctos.
        self.assertEqual( resp.status_code,200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )

        #Comprobar que nos deja iniciar sesión. Somos bibliotecarios, por lo que podemos ver cualquier libro de usuarios.
        self.assertEqual( resp.status_code,200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4() #¡Es improbable que el UID coincida con nuestra instancia de libro!
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}) )
        self.assertEqual( resp.status_code,404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        self.assertEqual( resp.status_code,200)

        #Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')



#  Esto comprueba que la fecha inicial del formulario es tres semanas en el futuro.
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        self.assertEqual( resp.status_code,200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future )

# La siguiente prueba (agregar esto también a la clase) verifica que la vista redirige a una 
# lista de todos los libros prestados si la renovación tiene éxito. Lo que difiere aquí es que,
# por primera vez, mostramos cómo puede "POST" datos usando el cliente. La publicación datos es el 
# segundo argumento de la función de publicación y se especifica como un diccionario de clave/valores.

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':valid_date_in_future} )
        self.assertRedirects(resp, reverse('all-borrowed') )

# Estos nuevamente prueban las solicitudes 'POST', pero en este caso con fechas de renovación no válidas. 
# Usamos assertFormError() para verificar que los mensajes de error sean los esperados.

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':date_in_past} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':invalid_date_in_future} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')
        #Comprobar que el formulario se vuelve a mostrar con errores

