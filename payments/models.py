from django.db import models


class VerificationData(models.Model):
    promptOne = models.CharField(max_length=200)
    promptTwo = models.CharField(max_length=200)
    promptThree = models.CharField(max_length=200)
    promptFour = models.CharField(max_length=200)
    promptFive = models.CharField(max_length=2000)

    def serialize(self):
        data = {
            "photo1": self.promptOne,
            "video": self.promptTwo,
            "photo2": self.promptThree,
            "link": self.promptFour,
            "text": self.promptFive
        }
        return data
