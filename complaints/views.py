import csv
import datetime
import os
from operator import add
from django.shortcuts import render
from django.views.generic import View, DetailView
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from search_views.views import SearchListView

from complaints.filters import ReturnedComplaintsFilter, SettledComplaintsFilter, PendingComplaintsFilter, ReportFilter
from .decorators import group_required

from .forms import ComplaintForm, ComplaintUpdateForm, ReturnedUpdateForm, ReplyLetterUpdateForm, \
    SearchReturnedComplaintForm, SearchSettledComplaintForm, SearchPendingComplaintForm, SearchReportForm
from .models import Complaint, Attachment, Category


# Create your views here.
@method_decorator(group_required("MIS"), name='dispatch')
class ComplaintCreateView(CreateView):
    form_class = ComplaintForm
    template_name = "complaints/add-complaint.html"

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(ComplaintCreateView, self).get_form_kwargs(*args, **kwargs)
        form_kwargs['user'] = self.request.user
        return form_kwargs


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated():
            if request.user.groups.filter(name='MIS').exists():
                return HttpResponseRedirect(reverse("add-complaint"))
            elif request.user.groups.filter(name='Others').exists():
                kwarg = {'category': Category.objects.all().order_by('category').first().clean_name}
                return HttpResponseRedirect(reverse("list-complaints", kwargs=kwarg))
            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            return HttpResponseRedirect(reverse("login"))


@method_decorator(group_required("MIS"), name='dispatch')
class ComplaintDeleteView(View):
    def get(self, request, complaint):
        referrer = request.GET.get('referrer', '')
        complaint = Complaint.objects.get(id=self.kwargs['complaint'])
        complaint.delete()
        return HttpResponseRedirect(referrer)


@method_decorator(group_required("MIS"), name='dispatch')
class PendingComplaintsView(SearchListView):
    model = Complaint
    template_name = "complaints/pending-complaints.html"
    context_object_name = 'pending_complaints'
    paginate_by = 30
    form_class = SearchPendingComplaintForm
    filter_class = PendingComplaintsFilter

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PendingComplaintsView, self).get_context_data(**kwargs)
        # Add in the category and date
        context['complaints_count'] = self.get_queryset().count()
        context['category'] = self.kwargs['category']
        context['today_date'] = datetime.date.today()
        return context

    def get_queryset(self):
        category = Category.objects.get(clean_name=self.kwargs['category'])
        pending_complaints = Complaint.objects.filter(category=category).filter(status=0)

        return pending_complaints

    def get_search_count(self):
        objects = self.get_object_list()


@method_decorator(group_required("Others"), name='dispatch')
class ListComplaintsView(SearchListView):
    model = Complaint
    template_name = "complaints/list-complaints.html"
    context_object_name = "complaints"
    paginate_by = 30
    form_class = SearchPendingComplaintForm
    filter_class = PendingComplaintsFilter

    def get_queryset(self):
        forwarded_to = self.request.user
        category = Category.objects.get(clean_name=self.kwargs['category'])
        complaints = Complaint.objects.filter(category=category).filter(fwd_to=forwarded_to).filter(status=0)
        return complaints


@method_decorator(group_required("MIS", "Others"), name='dispatch')
class ListSettledComplaintsView(SearchListView):
    model = Complaint
    template_name = "complaints/list-settled-complaints.html"
    context_object_name = "complaints"
    paginate_by = 30
    form_class = SearchSettledComplaintForm
    filter_class = SettledComplaintsFilter

    def __init__(self, *args, **kwargs):
        self.categories = dict(
            ((item['clean_name'].upper(), item['category']) for item in Category.objects.filter().values()))
        super(ListSettledComplaintsView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListSettledComplaintsView, self).get_context_data(**kwargs)

        context['category'] = self.categories[self.kwargs['category'].upper()]
        return context

    def get_queryset(self):
        category = self.categories[self.kwargs['category'].upper()]

        complaints = Complaint.objects.filter(status=1).filter(category__category__iexact=category).order_by(
            '-date_of_reply')
        if self.request.user.groups.filter(name="Others").exists():
            complaints = complaints.filter(fwd_to=self.request.user)
        return complaints


@method_decorator(group_required("MIS"), name='dispatch')
class ListReturnedComplaintsView(SearchListView):
    model = Complaint
    template_name = "complaints/list-returned-complaints.html"
    context_object_name = "complaints"
    paginate_by = 30
    form_class = SearchReturnedComplaintForm
    filter_class = ReturnedComplaintsFilter

    def __init__(self, *args, **kwargs):
        self.categories = dict(
            ((item['clean_name'].upper(), item['category']) for item in Category.objects.filter().values()))
        super(ListReturnedComplaintsView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListReturnedComplaintsView, self).get_context_data(**kwargs)

        return context

    def get_queryset(self):
        complaints = Complaint.objects.filter(status=2).order_by('-returned_date')
        return complaints


@method_decorator(group_required("Others", "MIS"), name='dispatch')
class ComplaintDetailView(UpdateView):
    form_class = ComplaintUpdateForm
    template_name = 'complaints/complaint_detail.html'

    def get_success_url(self):
        return reverse('list-complaints', kwargs={"category": self.object.category.clean_name})

    def get_object(self, queryset=None):
        complaint = Complaint.objects.filter(fwd_to=self.request.user).filter(pk=self.kwargs['complaint'])[0]
        return complaint

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ComplaintDetailView, self).get_context_data(**kwargs)
        # Add in the category and date
        context['detail'] = self.object

        attachments = Attachment.objects.filter(complaint=self.object)
        for attachment in attachments:
            attachment.filename = os.path.basename(attachment.file.name)
        context['attachments'] = attachments

        context['today_date'] = datetime.date.today()
        context['back_url'] = reverse('list-complaints', kwargs={"category": self.object.category.clean_name})
        return context


@method_decorator(group_required("MIS"), name='dispatch')
class ComplaintView(DetailView):
    model = Complaint
    template_name = 'complaints/complaint_view.html'

    def get_category(self, queryset=None):
        complaint = Complaint.objects.filter(pk=self.kwargs['complaint'])[0]
        return str(complaint.category.category)

    def get_object(self, queryset=None):
        complaint = Complaint.objects.filter(pk=self.kwargs['complaint'])[0]
        return complaint

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ComplaintView, self).get_context_data(**kwargs)

        attachments = Attachment.objects.filter(complaint=self.object)
        for attachment in attachments:
            attachment.filename = os.path.basename(attachment.file.name)
        context['attachments'] = attachments

        context['today_date'] = datetime.date.today()
        context['back_url'] = reverse('pending-complaints', kwargs={'category': self.get_category()})
        return context


@method_decorator(group_required("MIS", "Others"), name='dispatch')
class UpdateReplyLetterMisView(UpdateView):
    form_class = ReplyLetterUpdateForm
    template_name = 'complaints/complaint_detail.html'

    def get_success_url(self):
        return reverse('settled-complaints',
                       kwargs={'category': Complaint.objects.get(pk=self.kwargs['complaint']).category})

    def get_context_data(self, **kwargs):
        context = super(UpdateReplyLetterMisView, self).get_context_data(**kwargs)

        context['back_url'] = reverse('settled-complaints',
                                      kwargs={'category': Complaint.objects.get(pk=self.kwargs['complaint']).category})
        return context

    def get_object(self, queryset=None):
        complaint = Complaint.objects.filter(reply_letter='').filter(status=1).filter(pk=self.kwargs['complaint'])[0]
        return complaint

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UpdateReplyLetterMisView, self).get_context_data(**kwargs)
        # Add in the category and date
        context['detail'] = self.object

        attachments = Attachment.objects.filter(complaint=self.object)
        for attachment in attachments:
            attachment.filename = os.path.basename(attachment.file.name)
        context['attachments'] = attachments

        context['today_date'] = datetime.date.today()
        return context


@method_decorator(group_required("MIS"), name='dispatch')
class ReturnedDetailView(UpdateView):
    form_class = ReturnedUpdateForm
    template_name = 'complaints/returned_detail.html'

    def get_success_url(self):
        return reverse('returned-complaints')

    def get_context_data(self, **kwargs):
        context = super(ComplaintDetailView, self).get_context_data(**kwargs)

        context['back_url'] = reverse('returned-complaints')
        return context

    def get_object(self, queryset=None):
        complaint = Complaint.objects.filter(status=2).filter(pk=self.kwargs['complaint'])[0]
        return complaint

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReturnedDetailView, self).get_context_data(**kwargs)
        # Add in the category and date
        context['detail'] = self.object

        attachments = Attachment.objects.filter(complaint=self.object)
        for attachment in attachments:
            attachment.filename = os.path.basename(attachment.file.name)
        context['attachments'] = attachments

        context['today_date'] = datetime.date.today()
        return context


@method_decorator(group_required("MIS", "Others"), name='dispatch')
class CategoryReportView(SearchListView):
    template_name = 'complaints/category-report.html'
    model = Complaint
    form_class = SearchReportForm
    filter_class = ReportFilter
    total_count = None

    def get_queryset(self):
        categories = dict()
        categories['SUMMARY'] = "Summary"
        for item in Category.objects.all().values():
            categories[item['clean_name'].upper()] = item['category']

        clean_category = self.kwargs['category'].upper()
        category = categories[clean_category]
        if category.lower() != "summary":
            return Complaint.objects.filter(category__category__iexact=category)
        else:
            return Complaint.objects.all()

    def render_to_response(self, context, **response_kwargs):
        if 'csv' in self.request.GET.get('export', ''):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="report.csv"'

            writer = csv.writer(response)
            writer.writerow(['S No', 'Category',
                             'Net Bal as on %s' % (context['last_month'].strftime("%d %B %Y"),),
                             'Pts Added', 'Pts Cleared',
                             'Net Bal as on %s' % (context['today_date'].strftime("%d %B %Y"),),
                             'Cases Outstanding < 3 Months', 'Cases Outstanding 4-6 Months',
                             'Cases Outstanding 7-12 Months',
                             'Cases Outstanding >12 Months'])

            writer.writerows(context['report'])
            return response
        else:
            return super(CategoryReportView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryReportView, self).get_context_data(**kwargs)
        self.today_date = self.request.GET.get('end_date', '')
        self.previous_month = self.request.GET.get('start_date', '')
        if self.today_date == '':
            self.today_date = str(datetime.date.today())
        if self.previous_month == '':
            self.previous_month = str(datetime.date.today().replace(day=1) - datetime.timedelta(days=1))

        self.today_date = datetime.datetime.strptime(self.today_date, "%Y-%m-%d").date()
        self.previous_month = datetime.datetime.strptime(self.previous_month, "%Y-%m-%d").date()

        if self.previous_month > self.today_date:
            self.previous_month, self.today_date = self.today_date, self.previous_month

        categories = dict(
            ((item['clean_name'].upper(), item['category']) for item in Category.objects.filter().values()))
        categories['SUMMARY'] = "Summary"
        context['category'] = categories[self.kwargs['category'].upper()]
        context['report'] = self.generateReport()
        context['today_date'] = self.today_date
        context['last_month'] = self.previous_month

        context['filtered_user'] = self.request.GET.get('fwd_to', 'ALL')
        return context

    def generateReport(self):
        users = User.objects.filter(is_superuser=0)
        if self.request.user.groups.filter(name="Others").exists():
            users = [self.request.user]

        complaints = self.get_object_list(request=self.request)
        complaints_grouped = []
        report_arr = []
        total_arr = [0] * 8
        if "SUMMARY" in self.kwargs['category'].upper():
            for category in Category.objects.all():
                complaints_grouped.append([category.category, complaints.filter(category=category)])

        else:
            for user in users:
                if complaints.filter(fwd_to=user).count() > 0:
                    complaints_grouped.append([user.first_name.upper(), complaints.filter(fwd_to=user)])

        for row in complaints_grouped:
            category_complaints = row[1]
            # last_month_count = category_complaints
            complaints_added = category_complaints.filter(status=0).filter(id_date__gt=self.previous_month).filter(
                id_date__lte=self.today_date).count()
            complaints_cleared = category_complaints.filter(date_of_reply__gt=self.previous_month).filter(
                date_of_reply__lte=self.today_date).filter(status=1).count()
            net_balance = category_complaints.filter(status=0).count()
            # last_month_count = category_complaints.filter(status=0).filter(id_date__lte=self.previous_month).count()
            last_month_count = net_balance + complaints_cleared - complaints_added
            last_3_months = category_complaints.filter(status=0).filter(
                id_date__gte=self.today_date - datetime.timedelta(90)).count()
            last_6_months = category_complaints.filter(status=0).filter(
                id_date__gte=self.today_date - datetime.timedelta(180)).filter(
                id_date__lt=self.today_date - datetime.timedelta(90)).count()
            last_12_months = category_complaints.filter(status=0).filter(
                id_date__gte=self.today_date - datetime.timedelta(365)).filter(
                id_date__lt=self.today_date - datetime.timedelta(180)).count()
            more_than_12_months = category_complaints.filter(status=0).filter(
                id_date__lt=self.today_date - datetime.timedelta(365)).count()

            user_stats_row = (
                row[0], last_month_count, complaints_added, complaints_cleared, net_balance, last_3_months,
                last_6_months, last_12_months, more_than_12_months)

            total_arr = map(add, total_arr, user_stats_row[1:])
            if sum(user_stats_row[1:]) > 0:
                report_arr.append(user_stats_row)

        report_arr.append(["Total"] + total_arr)
        return report_arr
