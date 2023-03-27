from django.conf import settings
from django.core.paginator import Paginator


def get_padginator(queryset, request):
    """Функция паджинатора."""
    paginator = Paginator(queryset, settings.NUM_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
