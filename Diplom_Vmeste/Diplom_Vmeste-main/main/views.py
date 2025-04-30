from django.shortcuts import render, get_object_or_404, redirect
import random
from django.http import Http404

from . import models
from .models import Test, TestQuestion, QuestionOption, UserAnswer, TestResult, User, Topic, ChatSession, PostAuthor, SecurityPost
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import timezone
from datetime import timedelta
from .scenarios import SCENARIOS, MESSAGES, CHOICES, FOLLOWUPS, SCENARIO_RESULTS


def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def password(request):
    return render(request, 'main/password.html')

def tests(request):
    test = Test.objects.all()
    return render(request, 'main/tests.html', {'tests': test})



from .forms import UserForm


def start_test(request, test_id):
    # Очищаем предыдущие данные сессии
    request.session.flush()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['user_id'] = user.id
            request.session['user_data_submitted'] = True
            request.session['last_activity'] = str(timezone.now())
            return redirect('test_detail', test_id=test_id)
    else:
        form = UserForm()

    return render(request, 'main/start_test.html', {'form': form})

def check_session_activity(request):
    last_activity_str = request.session.get('last_activity')
    if last_activity_str:
        last_activity = timezone.datetime.fromisoformat(last_activity_str)
        if timezone.now() - last_activity > timedelta(seconds=300):
            request.session.flush()
            return False
    request.session['last_activity'] = str(timezone.now())
    return True

def test_detail(request, test_id):
    if not request.session.get('user_data_submitted'):
        return redirect('start_test', test_id=test_id)

        # Проверка активности сессии
    if not check_session_activity(request):
        return redirect('session_expired')

    test = get_object_or_404(Test, id=test_id)
    questions = list(test.testquestion_set.all().order_by('order').prefetch_related('questionoption_set'))

    session_key = f'test_{test_id}_progress'

    # Инициализация сессии с защитой от отсутствующих ключей
    if request.method == 'GET':
        if 'question' not in request.GET or not request.session.get(session_key):
            request.session[session_key] = {
                'current_question': 0,
                'answers': {}
            }

    # Получаем прогресс с значениями по умолчанию
    progress = request.session.get(session_key, {
        'current_question': 0,
        'answers': {}
    })

    # Приводим current_question к int на случай corrupted session data
    current_index = int(progress.get('current_question', 0))

    # Защита от выхода за пределы списка вопросов
    if current_index >= len(questions):
        return redirect('test_result', test_id=test.id)

    if request.method == 'POST':
        question = questions[current_index]
        selected_options = []

        try:
            if question.is_multiple_choice():
                selected_ids = request.POST.getlist(f'question_{question.id}[]', [])
                selected_options = QuestionOption.objects.filter(id__in=selected_ids)
            else:
                selected_id = request.POST.get(f'question_{question.id}')
                if selected_id:
                    selected_options = [QuestionOption.objects.get(id=selected_id)]

            # Обновляем answers с проверкой существования ключа
            answers = progress.get('answers', {})
            answers[str(question.id)] = [opt.id for opt in selected_options]
            progress['answers'] = answers

            # Обновляем сессию
            request.session[session_key] = progress

            # Переход к следующему вопросу
            if current_index + 1 < len(questions):
                progress['current_question'] = current_index + 1
                request.session[session_key] = progress
                return redirect(f'{request.path}?question={current_index + 1}')

            # Обработка завершения теста
            total_score = 0
            max_score = sum(q.score for q in questions)
            user_id = request.session.get('user_id')

            if user_id:
                user = User.objects.get(id=user_id)
                UserAnswer.objects.filter(user=user, test=test).delete()

                for q in questions:
                    correct_options = set(q.questionoption_set.filter(is_correct=True).values_list('id', flat=True))
                    user_answers = set(progress.get('answers', {}).get(str(q.id), []))

                    if user_answers == correct_options:
                        total_score += q.score

                    # Сохраняем все ответы
                    for opt_id in user_answers:
                        UserAnswer.objects.create(
                            user=user,
                            test=test,
                            question=q,
                            option=QuestionOption.objects.get(id=opt_id)
                        )

                TestResult.objects.create(
                    user=user,
                    test=test,
                    score=total_score,
                    max_score=max_score
                )

            # Очистка сессии
            if session_key in request.session:
                del request.session[session_key]

            return redirect('test_result', test_id=test.id)

        except Exception as e:
            # Логирование ошибки
            print(f"Error processing question: {e}")
            return redirect('test_detail', test_id=test_id)

    try:
        current_question = questions[current_index]
    except IndexError:
        return redirect('test_result', test_id=test.id)

    return render(request, 'main/test_details.html', {
        'test': test,
        'question': current_question,
        'progress': {
            'current': current_index + 1,
            'total': len(questions)
        }
    })


# main/views.py
def test_result(request, test_id):
    # существующий код получения данных
    if not request.session.get('user_data_submitted'):
        return redirect('start_test', test_id=test_id)

        # Проверка активности сессии
    if not check_session_activity(request):
        return redirect('session_expired')
    test = get_object_or_404(Test, id=test_id)
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('start_test', test_id=test_id)

    try:
        user = User.objects.get(id=user_id)
        result = TestResult.objects.filter(
            user=user,
            test=test
        ).latest('created_at')

        # Анализ результатов по темам
        topics_stats = {}
        questions = TestQuestion.objects.filter(test=test).prefetch_related('questionoption_set')

        for question in questions:
            if not question.topic:
                continue

            # Получаем правильные ответы
            correct_options = set(question.questionoption_set.filter(is_correct=True).values_list('id', flat=True))

            # Получаем ответы пользователя
            user_answers = set(UserAnswer.objects.filter(
                user=user,
                question=question
            ).values_list('option__id', flat=True))

            # Проверяем правильность
            is_correct = (user_answers == correct_options)

            # Обновляем статистику
            if question.topic.id not in topics_stats:
                topics_stats[question.topic.id] = {
                    'topic': question.topic,
                    'total': 0,
                    'correct': 0
                }

            topics_stats[question.topic.id]['total'] += 1
            if is_correct:
                topics_stats[question.topic.id]['correct'] += 1

        # Определяем слабые темы (<80%)
        weak_topics = []
        for stat in topics_stats.values():
            if stat['total'] > 0:
                correct_percent = (stat['correct'] / stat['total']) * 100
                if correct_percent < 80:
                    weak_topics.append({
                        'topic': stat['topic'],
                        'correct_percent': round(correct_percent, 1),
                        'resources': stat['topic'].resources
                    })

    except (User.DoesNotExist, TestResult.DoesNotExist):
        return redirect('start_test', test_id=test_id)

    return render(request, 'main/test_result.html', {
        'test': test,
        'result': result,
        'weak_topics': weak_topics
    })

def session_expired(request):
    request.session.flush()
    return render(request, 'main/session_expired.html')
def logout_user(request):
    request.session.flush()
    return redirect('index')

def scenario_list(request):
    return render(request, 'main/scenario_list.html', {'scenarios': SCENARIOS})

def scenario_chat(request, sc_id):
    scenario = next((s for s in SCENARIOS if s['id']==sc_id), None)
    if not scenario:
        raise Http404("Сценарий не найден")
    messages = MESSAGES.get(sc_id, [])
    choices  = CHOICES.get(sc_id, [])
    followups = FOLLOWUPS.get(sc_id, {})
    results = SCENARIO_RESULTS.get(sc_id, {})
    
    return render(request, 'main/scenario_chat.html', {
        'scenario':  scenario,
        'messages':  messages,
        'choices':   choices,
        'followups': followups,
        'results': results,
    })

def scenario_answer(request, sc_id):
    if request.method=='POST':
        choice = request.POST.get('choice')
        # примитивная валидация
        correct = choice=='safe'
        return render(request, 'main/scenario_result.html', {'correct': correct})
    return redirect('scenario_list')


def post_feed(request):
    posts = SecurityPost.objects.all().order_by('-created_at')
    return render(request, 'main/post_feed.html', {'posts': posts})


def check_post(request, post_id):
    post = get_object_or_404(SecurityPost, id=post_id)
    result = None

    if request.method == 'POST':
        choice = request.POST.get('choice')
        if choice in ['safe', 'danger']:
            result = {
                'is_correct': (choice == 'danger' and post.is_trap) or
                              (choice == 'safe' and not post.is_trap),
                'explanation': post.danger_explanation if post.is_trap else post.safe_explanation,
                'user_choice': choice
            }

    return render(request, 'main/post_feed.html', {
        'posts': SecurityPost.objects.all().order_by('-created_at'),
        'current_post': post,
        'result': result
    })

def random_scenario(request):
    """Перенаправляет на случайный сценарий из списка доступных"""
    if not SCENARIOS:
        raise Http404("Сценарии не найдены")
    
    # Выбираем случайный сценарий из списка
    random_scenario = random.choice(SCENARIOS)
    # Перенаправляем на страницу с этим сценарием
    return redirect('scenario_chat', sc_id=random_scenario['id'])