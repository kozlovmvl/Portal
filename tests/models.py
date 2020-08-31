from django.db import models
from django.db.models import Count, OuterRef, Exists, F, Prefetch
from django.utils import timezone

from authentication.models import CustomUser

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
    def is_exist(cls, test_id):
        try:
            return cls.objects.get(id=test_id, is_visible=True)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_list(cls, user):
        subquery = Attempt.objects.filter(user=user, test_id=OuterRef('id')).values('user')
        return list(cls.objects.values(
            'id', 'title', 'preview')
            .filter(is_visible=True)
            .annotate(available_attempts=~Exists(subquery)))

    @classmethod
    def get_one(cls, test_id):
        try:
            return cls.objects.values(
                'id', 'title', 'min_result', 'time',
                num_question=Count('tests')).get(id=test_id)
        except cls.DoesNotExist:
            return {'error': 'object is not find'}

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
        related_name="tests", on_delete=models.CASCADE)

    @classmethod
    def count(cls, test_id):
        return cls.objects.filter(test_id=test_id).count()

    @classmethod
    def get_questions(cls, test_id):
        # TODO: неоптимальный алгоритм сбора опций - слишком много запросов в БД.
        # TODO: переделать с помощью prefetch_related
        qs = Option.objects.all()
        questions = list(cls.objects.values('id', 'text', 'type').filter(test_id=test_id))
        options = cls.objects.prefetch_related(
            Prefetch('options', queryset=qs, to_attr="opts")
        ).filter(test_id=test_id)

        for i, item in enumerate(options):
            questions[i]['options'] = {opt.id: opt.text for opt in item.opts}
        return questions

    @classmethod
    def get_list_id(cls, test_id):
        return cls.objects.values_list('id', flat=True).filter(test_id=test_id)

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

    @classmethod
    def get_list_right(cls, id_quest):
        obj = cls.objects.prefetch_related('question').values(
            'question_id', 'question__type', 'id', 'order'
        ).filter(question_id__in=id_quest, is_right=True).order_by('order')
        result = {}
        for item in obj:
            if item['question_id'] in result:
                result[item['question_id']]['values'].append(item['id'])
            else:
                result.setdefault(item['question_id'], 
                    {"type": item['question__type'], 'values': [item['id']]})
        return result


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
    def is_exist(cls, attempt_id):
        try:
            attempt = cls.objects.get(id=attempt_id)
        except cls.DoesNotExist:
            return None
        if attempt.start + timezone.timedelta(minutes=attempt.test.time) < timezone.now():
            return None
        return attempt

    @classmethod
    def create(cls, user, test_id):
        return cls.objects.values(
            'id','start', 'finish', 'is_over'
            ).get_or_create(user=user, test_id=test_id)
        
    def __str__(self):
        return f'"{self.test}" от {self.user}'

class Answer(models.Model):

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
    
    is_right = models.BooleanField('верность ответа')
    options = models.ManyToManyField('Option', through='Choice', through_fields=["answer", "option"])
    attempt = models.ForeignKey(
        'Attempt', verbose_name='попытка', 
        related_name='answers', on_delete=models.CASCADE)

    @classmethod
    def add(cls, user, attempt, answers):
        """
        1. Результат должен вычисляться по формуле 100 * число_верных / общее_число_вопросов
        пользователь прислать меньше ответов, чем всего было вопросов,
        поэтому total_count_question нужно вычислять не как количество ответов, а как количество вопросов.

        2. Вопросы с верными вариантами ответов нужно получать из БД заранее одним запросом.

        3. Проверка правильности ответа зависит от типа вопроса:
        если тип sort, то нужно сравнивать list опций, т.к. важен именно порядок,
        иначе - сравнивать set опций.
        """

        list_id = Question.get_list_id(attempt.test.id)
        total_count_question = len(list_id)
        list_right_question = Option.get_list_right(list_id)
        count_right_answers = 0

        for id_question, list_answers in answers.items():
            is_right = False
            if int(id_question) in list_right_question and \
                list_right_question[int(id_question)]['type'] == 'sort':
                if list_answers == list_right_question[int(id_question)]['values']:
                    count_right_answers += 1
                    is_right = True
            elif int(id_question) in list_right_question and \
                 set(list_right_question[int(id_question)]['values']) == set(list_answers):
                    count_right_answers += 1
                    is_right = True
            cls.create_answer(attempt, is_right, list_answers)
        result, status = cls.save_results(attempt, count_right_answers, total_count_question)
        return {'result': result, 'status': status}, 200

    @classmethod
    def save_results(cls, attempt, right_answ, count_qst):
        attempt.result = 100 * right_answ / count_qst
        attempt.is_over = True
        attempt.finish = timezone.now()
        status_test = True if attempt.test.min_result < attempt.result else False
        attempt.save(update_fields=['result', 'is_over', 'finish'])
        return attempt.result, status_test

    @classmethod
    def create_answer(cls, attempt, is_right, list_answers):
        obj = cls(attempt=attempt, is_right=is_right)
        obj.save()
        obj.options.add(*list_answers)
        return obj

    def __str__(self):
        return f'{self.attempt} {self.is_right}'


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