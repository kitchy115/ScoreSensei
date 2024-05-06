from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse

# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    print(instance.user.username)
    return "user_{0}/{1}".format(instance.user.id, filename)


class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score_title = models.CharField(max_length=100)
    score_slug = AutoSlugField(populate_from="score_title", unique_with="user")
    score_xml = models.FileField(max_length=500, upload_to=user_directory_path)
    score_json = models.FileField(max_length=500, upload_to=user_directory_path)

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
