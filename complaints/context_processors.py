from .models import Complaint

def categories(request):
    categories = Complaint.CATEGORY
    return {"categories":categories}