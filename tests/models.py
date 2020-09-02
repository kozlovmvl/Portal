from django.db import models
from django.db.models import Count, Case, When, Value, OuterRef, F
from django.utils import timezone

from authentication.models import CustomUser
import json

class Test(models.Model):

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
    
    title = models.CharField('название теста', max_length=255)
    preview = models.ImageField('превью', upload_to='upload/tests/preview/%Y/%m/%d/')
    is_visible = models.BooleanField('видимость')
    min_result = models.DecimalField('мин. результат', max_digits=100, decimal_places=1)
    time = models.PositiveIntegerField('время прохождения(мин)')

    @classmethod
    def get_list(cls, user):
        qs = cls.objects.exclude(test_attempts__user_id=user.id)\
            .filter(is_visible=True).order_by('title')\
            .values('id', 'title', 'preview')
        return list(qs)

    @classmethod
    def get_one(cls, test_id):
        return cls.objects.values(
            'id', 'title', 'min_result', 'time',
            num_question=Count('questions')).get(id=test_id)

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
    test = models.ForeignKey(
        'Test', verbose_name="из теста", 
        related_name="questions", on_delete=models.CASCADE)

    @classmethod
    def get_questions(cls, test_id):
        list_questions = []
        for q in cls.objects.filter(test_id=test_id)\
                .prefetch_related('options').order_by('order'):
            list_questions.append({
                'id': q.id,
                'text': q.text,
                'options': list(q.options.all().values_list('id', flat=True))
            })
        return list_questions

    @classmethod
    def get_right_options(cls, test_id):
        """
        Возвращает словарь:
        ключ: id вопроса,
        значение: {'type': str, 'options': list of int}
        """
        questions = {}
        for q in cls.objects.filter(test_id=test_id).prefetch_related('options'):
            right_options = []
            for opt in q.options.all().order_by('order'):
                if opt.is_right:
                    right_options.append(opt.id)
            questions[q.id] = {'type': q.type, 'options': right_options}
        return questions

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

    start = models.DateTimeField('дата начала', blank=True, null=True, auto_now_add=True)
    finish = models.DateTimeField('дата окончания', blank=True, null=True)
    result = models.DecimalField('результат', blank=True, null=True, max_digits=100, decimal_places=1)
    is_over = models.BooleanField('окончен?', default=False)
    test = models.ForeignKey(
        'Test', verbose_name="тест", 
        related_name='test_attempts', on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser, verbose_name="пользователь",
        related_name='attempts', on_delete=models.CASCADE)

    @classmethod
    def create(cls, user, test_id):
        return cls.objects.values(
            'id','start', 'finish', 'is_over'
            ).get_or_create(user=user, test_id=test_id)

    def is_expired(self):
        return self.start + timezone.timedelta(minutes=self.test.time) < timezone.now()

    def close(self, result):
        test = Test.get_one(self.test.id)
        self.result = result
        self.finish = timezone.now()
        self.is_over = True
        self.save(update_fields=['result', 'finish', 'is_over', ])
        return True if test['min_result'] < result else False

    @classmethod
    def get_list(cls, **kwargs):            
        list_obj = list(cls.objects.values('result', 
        is_success=Case(
            When(test__min_result__gt=F('result'), then=Value(False)),
            When(result__isnull=True, then=Value(False)),
            default=Value(True),
            output_field=models.BooleanField()
        )
        ).filter(**kwargs))
        return list_obj

    def __str__(self):
        return f'"{self.test}" от {self.user}'


class Answer(models.Model):

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
    
    is_right = models.BooleanField('верность ответа')
    options = models.ManyToManyField(
        'Option', through='Choice', through_fields=["answer", "option"])
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    @classmethod
    def add(cls, user, attempt, answers):
        answers = json.loads(answers)
        questions = Question.get_right_options(attempt.test_id)
        rights_count = 0
        for q_id, option_ids in answers.items():
            if questions[int(q_id)]['type'] == 'sort':
                is_right = questions[int(q_id)]['options'] == option_ids
            else:
                is_right = set(questions[int(q_id)]['options']) == set(option_ids)
            ans_obj = cls.objects.create(question_id=int(q_id), is_right=is_right)
            bulk = []
            for opt_id in option_ids:
                bulk.append(Choice(answer_id=ans_obj.id, option_id=opt_id))
            Choice.objects.bulk_create(bulk)
            if is_right:
                rights_count += 1
        return 100 * rights_count / len(questions)

    def __str__(self):
        return f'{self.question_id} {self.is_right}'


class Choice(models.Model):

    class Meta:
        verbose_name = 'выбор'
        verbose_name_plural = 'выборы'

    answer = models.ForeignKey(
        'Answer', on_delete=models.CASCADE,
        related_name='answers_choices', verbose_name='ответ')
    option = models.ForeignKey(
        'Option', on_delete=models.CASCADE,
        related_name='options_choices', verbose_name='опция')
    
    def __str__(self):
        return f'{self.answer} - ответ: {self.option}'
