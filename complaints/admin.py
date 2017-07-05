import re

from django.contrib import admin
from complaints.models import Category, Complaint
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('clean_name',)

    def save_model(self, request, obj, form, change):
        obj.clean_name =  re.sub('[^0-9a-zA-Z]+', '', obj.category)
        super(CategoryAdmin, self).save_model(request, obj, form, change)


class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('petition_id_no', 'id_date', 'pending_since', 'category', 'fwd_to')

admin.site.register(Complaint, ComplaintAdmin)