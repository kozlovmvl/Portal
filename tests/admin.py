from django.contrib import admin

from .models import *


#admin.site.register(Test)
admin.site.register(Answer)
admin.site.register(Attempt)
admin.site.register(Choice)

class QuestionsInline(admin.TabularInline):
    model = Question
    extra = 0

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

@admin.register(Test)
class TestsAdmin(admin.ModelAdmin):
    inlines = [QuestionsInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
