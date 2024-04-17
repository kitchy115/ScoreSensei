from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "type": "text",
                "class": "form-style",
                "placeholder": "Username",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "type": "password",
                "class": "form-style",
                "placeholder": "Password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "type": "password",
                "class": "form-style",
                "placeholder": "Confirm Password",
            }
        )

        """
        self.fields["filename"].widget.attrs.update(
            {
                "type": "filename",
                "class": "form-style",
                "placeholder": "Enter a filename",
            }
        )
        """

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


"""
class FileCreation(FileCreationForm):

"""