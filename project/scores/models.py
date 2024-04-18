from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.


class Score(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default="",
    )
    title = models.CharField(
        max_length=100,
        default="",
    )
    slug = models.SlugField(unique=True)
    # score_file = models.FileField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Score, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("read_score", kwargs={"slug": self.slug})
