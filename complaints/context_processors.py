from .models import Complaint, Category


def categories(request):
    categories = Category.objects.all().order_by('category')
    category_array = []
    for category in categories:
        category_array.append((category.clean_name, category.category))
    return {"categories":category_array}