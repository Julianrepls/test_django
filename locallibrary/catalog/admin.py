from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookInstance

# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)

class BooksInline(admin.TabularInline):  # ---------->U
    model = Book #------->U

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] #esto mostraría los campos en vertial pero como hemos usado una tupla lo muestra en horizontal.
    inlines = [BooksInline] #----------> U
# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


"""
    En este caso, todo lo que hemos hecho es declarar nuestra clase encadenada tabular,
    que simplemente añade todos los campos del modelo encadenado. Puedes especificar toda clase 
    de información adicional para el diseño incluyendo los campos a mostrar, su órden, si son solo
    de lectura o no, etc. (ve TabularInline para más información). lo vemos a continuación:
"""


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


# Register the Admin classes for Book using the decorator

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]




# Register the Admin classes for BookInstance using the decorator
# listamos campos en el atributo list_filter: Una vez que tienes muchos ítems en una lista, puede ser útil filtrar los ítems que se despliegan

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book','status', 'due_back', 'id') # -----------> U
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )
