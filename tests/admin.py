from django.contrib import admin

from .models import *


admin.site.register(Test)

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
