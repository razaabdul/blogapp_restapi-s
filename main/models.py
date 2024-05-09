from django.db import models
from django.contrib.auth.models import User
import uuid

class Base(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Blog(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs", blank=True, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    main_image = models.ImageField(upload_to='blogs/', null=True, blank=True)


class Comment(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", blank=True, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,
                 related_name='blog_comments')# reverse relationship
    text = models.TextField()

class Like(Base):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    value=models.IntegerField(default=0)

