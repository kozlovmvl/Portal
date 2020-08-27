from django.db import models

from authentication.models import CustomUser

class Test(models.Model):

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
    
    title = models.CharField('название теста', max_length=255)
    preview = models.ImageField('превью', upload_to='upload/tests/preview/%Y/%m/%d/')
    is_visible = models.BooleanField('видимость')
    min_result = models.DecimalField('мин. результат', max_digits=100, decimal_places=1)

    def __str__(self):
        return self.title


class Question(models.Model):

    CHOICES = [
        ('radio', 'radio'),
        ('checkbox', 'checkbox'),
        ('sort', 'sort')
    ]

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    type = models.CharField('тип поля', max_length=8, choices=CHOICES)
    text = models.TextField('текст')
    order = models.PositiveIntegerField('порядок')

    def __str__(self):
        if len(self.text) > 70:
            return f'{self.text[:70]}...'
        return self.text


class Option(models.Model):

    class Meta:
        verbose_name = 'опция'
        verbose_name_plural = 'опции'

    text = models.TextField('текст')
    is_right = models.BooleanField('верность ответа')
    order = models.PositiveIntegerField('порядок')
    question = models.ForeignKey(
        'Question', verbose_name='вопрос',
        related_name='options', on_delete=models.CASCADE)

    def __str__(self):
        if len(self.text) > 70:
            return f'{self.text[:70]}...'
        return self.text


class Attempt(models.Model):

    class Meta:
        verbose_name = 'попытка'
        verbose_name_plural = 'попытки'

    start = models.DateTimeField('дата начала', auto_now_add=True)
    finish = models.DateTimeField('дата окончания')
    result = models.DecimalField('результат', max_digits=100, decimal_places=1)
    is_over = models.BooleanField('окончен?')
    user = models.ForeignKey(
        CustomUser, verbose_name="пользователь",
        related_name='attempts', on_delete=models.CASCADE)


class Answer(models.Model):

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
    
    is_right = models.BooleanField('верность ответа')
    options = models.ManyToManyField('Option')
    attempt = models.ForeignKey(
        'Attempt', verbose_name='попытка', 
        related_name='answers', on_delete=models.CASCADE)


class Choice(models.Model):

    class Meta:
        verbose_name = 'выбор'
        verbose_name = 'выборы'

    answer = models.ForeignKey(
        'Answer', on_delete=models.CASCADE,
        related_name='answers_choices', verbose_name='ответ')
    option = models.ForeignKey(
        'Option', on_delete=models.CASCADE,
        related_name='options_choices', verbose_name='опция')