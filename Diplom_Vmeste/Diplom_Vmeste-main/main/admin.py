from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(UserCrime)
admin.site.register(Test)
admin.site.register(TestQuestion)
admin.site.register(QuestionOption)
admin.site.register(UserAnswer)
admin.site.register(TestResult)
admin.site.register(SecurityPost)
admin.site.register(PostAuthor)
admin.site.register(QuestionTopic)