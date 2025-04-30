from datetime import timezone
import uuid
from django.db import models

#Пользователь
class User(models.Model):
    AGE_CHOICES = [
        ('<18', 'Менее 18 лет'),
        ('18-25', '18-25 лет'),
        ('26-35', '26-35 лет'),
        ('36-50', '36-50 лет'),
        ('51-64', '51-64 лет'),
        ('65+', 'Более 65 лет'),
    ]

    GENDER_CHOICES = [
        ('F', 'Женский'),
        ('M', 'Мужской'),
    ]

    EDUCATION_CHOICES = [
        ('basic', 'Основное общее (до 9 класса)'),
        ('secondary', 'Среднее общее (до 11 класса)'),
        ('college', 'Среднее специальное'),
        ('higher', 'Высшее'),
        ('phd', 'Ученая степень'),
        ('none', 'Отсутствует'),
    ]

    CAREER_CHOICES = [
        ('student', 'Учащийся/Студент'),
        ('it', 'IT/Технологии'),
        ('gov', 'Госслужба'),
        ('military', 'Военная служба'),
        ('edu', 'Образование/Наука'),
        ('health', 'Здравоохранение'),
        ('law', 'Правоохранительные органы'),
        ('services', 'Услуги'),
        ('business', 'Предпринимательская деятельность'),
        ('retired', 'Пенсионер'),
        ('housewife', 'Домохозяйка/молодая мама'),
        ('unemployed', 'Временно не работающий'),
        ('engineer', 'Инженер'),
        ('worker', 'Рабочий'),
        ('sales', 'Продажи'),
        ('creative', 'Творчество'),
        ('agriculture', 'Сельское хозяйство'),
        ('media', 'Медиа'),
    ]

    INTERNET_CHOICES = [
        ('always', 'Постоянно'),
        ('1-3', '1-3 раза в день'),
        ('4-10', '4-10 раз в день'),
        ('rare', 'Реже'),
    ]

    AWARENESS_CHOICES = [
        ('none', 'Нулевой'),
        ('basic', 'Базовый'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    EXPERIENCE_CHOICES = [
        ('yes', 'Да'),
        ('no', 'Нет'),
        ('unsure', 'Не уверен(а)'),
    ]

    CRIME_CHOICES = [
        ('phishing', 'Фишинг'),
        ('fraud', 'Мошенничество с платежами'),
        ('hacking', 'Взлом аккаунтов'),
        ('viruses', 'Вирусное заражение'),
        ('bullying', 'Кибербуллинг/шантаж'),
        ('spam_calls', 'Мошеннические звонки'),
        ('social_fraud', 'Обман в соцсетях'),
    ]

    age = models.CharField(
        max_length=50,
        choices=AGE_CHOICES,
        blank=True,  # разрешаем пустое значение
        null=True  # если нужно хранить NULL в БД
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    education_level = models.CharField(
        max_length=50,
        choices=EDUCATION_CHOICES,
        blank=True,
        null=True
    )
    career = models.CharField(
        max_length=50,
        choices=CAREER_CHOICES,
        blank=True,
        null=True
    )
    internet_usage = models.CharField(
        max_length=50,
        choices=INTERNET_CHOICES,
        blank=True,
        null=True
    )
    awareness_level = models.CharField(
        max_length=50,
        choices=AWARENESS_CHOICES,
        blank=True,
        null=True
    )
    cyber_experience = models.CharField(
        max_length=50,
        choices=EXPERIENCE_CHOICES,
        blank=True,
        null=True
    )
    cyber_crimes = models.JSONField(default=list, blank=True)

class QuestionTopic(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название темы")
    description = models.TextField(verbose_name="Описание темы")
    resources = models.TextField(
        verbose_name="Рекомендации и ресурсы",
        help_text="Ссылки и материалы для изучения темы"
    )

    def __str__(self):
        return self.name
#Преступления с которыми сталкивался пользователь
class UserCrime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crimeType = models.CharField(max_length=100)

#Тест
class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    max_score = models.PositiveIntegerField(null=True, blank=True)
    def __str__(self):
        return self.title

#Вопросы
class TestQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question_text = models.TextField()
    score = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    topic = models.ForeignKey(
        QuestionTopic,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name="Тема вопроса")
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]

    def is_multiple_choice(self):
        return self.questionoption_set.filter(is_correct=True).count() > 1

#Ответы
class QuestionOption(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.option_text

#То что ответил пользователь
class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    answer_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Ответ на {self.question}"

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    max_score = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.test}: {self.score}/{self.max_score}"

#Чат с мошенником
class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()  # Описание темы обмана :contentReference[oaicite:0]{index=0}

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    choices = models.JSONField()       # Варианты ответа храним как JSON :contentReference[oaicite:1]{index=1}
    correct = models.CharField(max_length=100)

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    current_step = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ScriptedMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='scripted')
    step = models.IntegerField()       # Шаг диалога :contentReference[oaicite:2]{index=2}
    role = models.CharField(max_length=10, choices=[('scammer','Мошенник'),('user','Пользователь')])
    text = models.TextField()
    choices = models.JSONField(null=True, blank=True)
    # Маппинг {выбор: следующий шаг}
    next_steps = models.JSONField()

class PostAuthor(models.Model):
    name = models.CharField(max_length=100)
    avatar = models.URLField()  # URL сгенерированной аватарки
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.avatar:
            # Генерация уникальной аватарки на основе имени
            from django.utils.text import slugify
            import hashlib
            seed = slugify(self.name) or hashlib.md5(self.name.encode()).hexdigest()[:8]
            self.avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={seed}&size=100&backgroundColor=random"
        super().save(*args, **kwargs)

class SecurityPost(models.Model):
    author = models.ForeignKey(PostAuthor, on_delete=models.CASCADE)
    content = models.TextField()
    is_trap = models.BooleanField(default=False)  # Содержит ли пост угрозу
    danger_explanation = models.TextField()       # Объяснение опасности
    safe_explanation = models.TextField()         # Объяснение безопасности
    created_at = models.DateTimeField(auto_now_add=True)