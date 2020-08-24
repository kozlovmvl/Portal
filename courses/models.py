from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class Folder(models.Model):

    class Meta:
        verbose_name='Папка'
        verbose_name_plural='Папки'

    title = models.CharField('Папка', max_length=255)
    preview = models.ImageField('Превью')
    is_visible = models.BooleanField('Видимость', default=False)

    def __str__(self):
        return self.title

    @classmethod
    def get_list():
        responce = list(cls.objects.values('id', 'title', 'preview').order_by('title'))
        return {'folders': responce}


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
            responce = list(cls.objects.filter(folder=folder_id).values(
                'id', 'title', 'description', 'created', 'preview'))
            
            if len(responce):
                return {'documents': responce}
            else:
                return {'error': 'folder not exist'}

        except ValueError:
            return {'error': 'forder_id uncorrect'}

    @classmethod
    def get_one(cls, doc_id):
        try:
            doc_id = int(doc_id)

            elements = list(Element.objects.filter(doc=doc_id).order_by('order').values('text', 'type', 'file'))
            doc = cls.objects.values('title').get(pk=doc_id)
            doc['content'] = elements

            return doc
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


    def __str__(self):
        return self.type