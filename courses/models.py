from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class Folder(models.Model):

    class Meta:
        verbose_name='папка'
        verbose_name_plural='папки'

    title = models.CharField('Папка', max_length=255)
    preview = models.ImageField('Превью')
    is_visible = models.BooleanField('Видимость', default=False)

    def __str__(self):
        return self.title

    @classmethod
    def get_list(cls):
        list_obj = list(cls.objects.values('id', 'title', 'preview').order_by('title'))
        return {'folders': list_obj}


class Document(models.Model):
    class Meta:
        verbose_name='Документ'
        verbose_name_plural='Документы'

    title = models.CharField('Название документа', max_length=255)
    description = models.TextField('Описание')
    preview = models.ImageField('Превью')
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    is_visible = models.BooleanField('Видимость')
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @classmethod
    def get_list(cls, folder):
        try:
            folder_id = int(folder)
            list_obj = list(cls.objects.filter(folder=folder_id).values(
                'id', 'title', 'description', 'created', 'preview'))
            
            if len(list_obj):
                return {'documents': list_obj}
            else:
                return {'error': 'folder not exist'}
        except ValueError:
            return {'error': 'forder_id uncorrect'}

    @classmethod
    def get_one(cls, doc_id):
        try:
            obj = Element.get_list(doc_id)
            obj['title'] = cls.objects.values('title').get(pk=int(doc_id))
            return obj
        except ValueError:
            return {'error': 'doc_id is invalid'}
        except ObjectDoesNotExist:
            return {'error': 'id not find'}



class Element(models.Model):
    
    CHOICES = [
        ('html', 'html'),
        ('image', 'Изображение'),
        ('file', 'Файл'),
    ]

    class Meta:
        verbose_name = 'Элемент'
        verbose_name_plural = 'Элементы'

    doc = models.ForeignKey('Document', related_name="document", on_delete=models.CASCADE)
    type = models.CharField('Тип', max_length=5, choices=CHOICES)
    text = models.TextField('Текст')
    order = models.PositiveIntegerField('порядок')
    file = models.FileField('Файл', upload_to='upload/%Y/%m/%d/')


    @classmethod
    def get_list(cls, doc_id):
        try:
            get_list = list(cls.objects.filter(doc=int(doc_id)).order_by('order').values('text', 'type', 'file'))
            return {'content': get_list}
        except ValueError:
            return {'error': 'doc_id is invalid'}

    def __str__(self):
        return self.type