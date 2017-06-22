from django.contrib import admin
from .models import Message, Answer

# Register your models here.


class AnswerInline(admin.TabularInline):
    fields = ["answer_text", "publication_date"]
    model = Answer
    extra = 1


class AnswerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['answer_text']}),
        ('Date information', {'fields': ['publication_date']}),
    ]
    list_display = ('answer_text', 'publication_date', 'was_published_today')
    list_filter = ['publication_date']
    search_fields = ['answer_text']

admin.site.register(Answer, AnswerAdmin)


class MessageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['message_text']}),
        ('Date information', {'fields': ['publication_date'], 'classes': ['collapse']}),
    ]
    inlines = [AnswerInline]
    list_display = ('message_text', 'publication_date', 'was_published_today')
    list_filter = ['publication_date']
    search_fields = ['message_text']

admin.site.register(Message, MessageAdmin)
