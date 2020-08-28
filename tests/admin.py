from django.contrib import admin

from .models import *


admin.site.register(Test)
admin.site.register(Answer)
admin.site.register(Attempt)
admin.site.register(Choice)

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
