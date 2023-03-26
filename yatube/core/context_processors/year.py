from django.utils import timezone


def year(request):
    datetime = timezone.now().year
    return {
        'year': datetime
    }
