from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse

# Create your models here.


class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score_title = models.CharField(max_length=100)
    score_slug = AutoSlugField(populate_from="score_title", unique_with="user")
    score_xml = models.FileField()
    score_json = models.FileField()

    def save(self, *args, **kwargs):
        # check if the title already exists
        if Score.objects.filter(user=self.user, score_title=self.score_title).exists():
            suffix = 1
            while True:
                new_title = f"{self.score_title}-{suffix}"
                if not Score.objects.filter(
                    user=self.user, score_title=new_title
                ).exists():
                    self.score_title = new_title
                    break
                suffix += 1

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("read_score", kwargs={"slug": self.score_slug})
