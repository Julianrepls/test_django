import datetime
from django.utils import timezone

from catalog.models import BookInstance, Book, Genre
from django.contrib.auth.models import User #Obligatorio para asignar al usuario como prestatario

class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        #Crear dos usuarios
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        #Crear un libro
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author, language=test_language)
        # Crear género como un paso posterior
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) #No se permite la asignación directa de tipos de muchos a muchos.
        test_book.save()

        #Crea 30 objetos BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date= timezone.now() + datetime.timedelta(days=book_copy%5)
            if book_copy % 2:
                the_borrower=test_user1
            else:
                the_borrower=test_user2
            status='m'
            BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "exitosa"
        self.assertEqual(resp.status_code, 200)

        #Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')


    #Comprobar que la lista de libros prestados pertenece al usuario:
    
    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        #CComprueba que inicialmente no tenemos ningún libro en lista (ninguno en préstamo)
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual( len(resp.context['bookinstance_list']),0)

        #Ahora cambia todos los libros para que estén en préstamo
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status='o'
            copy.save()

        #Comprueba que ahora tenemos libros prestados en la lista
        resp = self.client.get(reverse('my-borrowed'))
        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        #Confirma que todos los libros pertenecen a testuser1 y están en préstamo
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        #Cambiar todos los libros para que estén en préstamo
        for copy in BookInstance.objects.all():
            copy.status='o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        #Confirma que de los artículos, solo se muestran 10 debido a la paginación.
        self.assertEqual( len(resp.context['bookinstance_list']),10)

        last_date=0
        for copy in resp.context['bookinstance_list']:
            if last_date==0:
                last_date=copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)

