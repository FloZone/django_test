from django.contrib import admin

from .models import Message, Author

# Register your models here.


class MessageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['message_text']}),
        ('Date information', {'fields': ['publication_date'], 'classes': ['collapse']}),
    ]
    list_display = ('message_text', 'publication_date', 'was_published_today')
    list_filter = ['publication_date']
    search_fields = ['message_text']

admin.site.register(Message, MessageAdmin)


class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['username', 'first_name', 'last_name', 'email', 'is_staff']}),
    ]
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    search_fields = ['username', 'first_name', 'last_name', 'email']

admin.site.register(Author, AuthorAdmin)
