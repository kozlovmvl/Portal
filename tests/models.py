from django.db import models

class Test(models.Model):

    class Meta:
        verbose_name = 'test'
        verbose_name_plural = 'tests'
    
    title = models.CharField('title', max_length=255)
    preview = models.ImageField('preview', upload_to='upload/tests/preview/%Y/%m/%d/')
    is_visible = models.BooleanField('is_visible')
    min_result = models.DecimalField('decimal', max_digits=100, decimal_places=1)

    def __str__(self):
        return self.title

class Question(models.Model):

    CHOICES = [
        ('radio', 'radio'),
        ('checkbox', 'checkbox'),
        ('sort', 'sort')
    ]

    class Meta:
        verbose_name = 'question'
        verbose_name_plural = 'questions'

    type = models.CharField('type', max_length=8, choices=CHOICES)
    text = models.TextField('text')
    order = models.PositiveIntegerField('order')

    def __str__(self):
        if len(self.text) > 70:
            return "{}...".format(self.text[:70])
        return self.text


class Option(models.Model):

    class Meta:
        verbose_name = 'option'
        verbose_name_plural = 'options'

    text = models.TextField('text')
    is_right = models.BooleanField('is_right')
    order = models.PositiveIntegerField('order')
    question = models.ForeignKey('Question', related_name="options", on_delete=models.CASCADE)

    def __str__(self):
        if len(self.text) > 70:
            return "{}...".format(self.text[:70])
        return self.text