from django.db import models


class Folder(models.Model):

    class Meta:
        verbose_name='папка'
        verbose_name_plural='папки'

    title = models.CharField('папка', max_length=255)
    preview = models.ImageField('превью')
    is_visible = models.BooleanField('видимость', default=False)

    def __str__(self):
        return self.title

    @classmethod
    def get_list(cls):
        return list(cls.objects.values('id', 'title', 'preview')
                    .order_by('title'))


class Document(models.Model):
    class Meta:
        verbose_name='документ'
        verbose_name_plural='документы'

    title = models.CharField('название документа', max_length=255)
    description = models.TextField('описание')
    preview = models.ImageField('превью')
    created = models.DateTimeField('дата создания', auto_now_add=True)
    is_visible = models.BooleanField('видимость')
    folder = models.ForeignKey(
        'Folder', verbose_name='папка', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @classmethod
    def get_list(cls, folder_id):
        return list(cls.objects.filter(folder=folder_id).values(
            'id', 'title', 'description', 'created', 'preview'))
            

    @classmethod
    def get_one(cls, doc_id):
        try:
            list_obj = Element.get_list(doc_id)
            obj = cls.objects.values('title').get(pk=doc_id)
            return {**obj, 'content': list_obj}, 200
        except ValueError:
            return {'error': 'doc_id is invalid'}, 400
        except cls.DoesNotExist:
            return {'error': 'id not find'}, 400


class Element(models.Model):
    
    CHOICES = [
        ('html', 'html'),
        ('image', 'изображение'),
        ('file', 'файл'),
    ]

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'

    doc = models.ForeignKey(
        'Document', verbose_name='документ',
        related_name='document', on_delete=models.CASCADE)
    type = models.CharField('тип', max_length=5, choices=CHOICES)
    text = models.TextField('текст')
    order = models.PositiveIntegerField('порядок')
    file = models.FileField('файл', upload_to='upload/%Y/%m/%d/')


    @classmethod
    def get_list(cls, doc_id):
        return list(cls.objects.filter(doc=doc_id).order_by('order')
                    .values('text', 'type', 'file'))

    def __str__(self):
        return self.type