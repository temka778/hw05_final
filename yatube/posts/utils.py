from django.core.paginator import Paginator


def page_navigation(posts, request):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
