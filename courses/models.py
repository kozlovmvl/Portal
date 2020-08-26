from django.db import models
from django.db.models import OuterRef, Count, Exists

from authentication.models import CustomUser

class Folder(models.Model):

    class Meta:
        verbose_name='папка'
        verbose_name_plural='папки'

    title = models.CharField('папка', max_length=255)
    preview = models.ImageField('превью', upload_to='upload/preview/%Y/%m/%d/')
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
    preview = models.ImageField('превью', upload_to='upload/preview/%Y/%m/%d/')
    created = models.DateTimeField('дата создания', auto_now_add=True)
    is_visible = models.BooleanField('видимость')
    views = models.PositiveIntegerField('просмотры', default=0)
    folder = models.ForeignKey(
        'Folder', verbose_name='папка', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @classmethod
    def get_list(cls, user, folder_id):
        subquery = LikeDocument.objects.filter(user=user, doc=OuterRef('id'))
        list_obj = list(cls.objects.filter(folder=folder_id).values(
            'id', 'title', 'description', 'created', 'preview', 'views'
            ).annotate(
                likes=Count('likes'),
            ).annotate(
                is_liked=Exists(subquery))
            )
        return list_obj
            

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
    
    @classmethod
    def create_or_update_views(cls, user, doc_id):
        doc = cls.objects.get(id=doc_id)
        view_doc, created = ViewDocument.objects.get_or_create(user=user, doc=doc)
        if created:
            doc.views += 1
            doc.save(update_fields=['views'])
        else:
            view_doc.save(update_fields=['date'])

        return created

            
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
        related_name='elements', on_delete=models.CASCADE)
    type = models.CharField('тип', max_length=5, choices=CHOICES)
    text = models.TextField('текст')
    order = models.PositiveIntegerField('порядок')
    file = models.FileField('файл', upload_to='upload/files/%Y/%m/%d/')


    @classmethod
    def get_list(cls, doc_id):
        return list(cls.objects.filter(doc=doc_id).order_by('order')
                    .values('text', 'type', 'file'))

    def __str__(self):
        return self.type


class ViewDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doc = models.ForeignKey('Document', related_name="view", verbose_name="документ", on_delete=models.CASCADE)
    date = models.DateTimeField('время просмотра', auto_now=True)

    def __str__(self):
        return "{}'ом просмотрен документ {}".format(self.user, self.doc)

class LikeDocument(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doc = models.ForeignKey('Document', related_name="likes", verbose_name="документ", on_delete=models.CASCADE)

    @classmethod
    def set_like(cls, user, doc_id):
        doc = Document.objects.get(id=doc_id)
        like_doc, created = cls.objects.get_or_create(user=user, doc=doc)
        return created
