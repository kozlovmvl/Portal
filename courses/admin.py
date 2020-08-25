from django.contrib import admin
from courses.models import *


# Register your models here.

admin.site.register(Folder)

class ElementInline(admin.TabularInline):
    model = Element
    extra = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_visible']
    search_fields = ['id', 'title']
    inlines = [ElementInline]