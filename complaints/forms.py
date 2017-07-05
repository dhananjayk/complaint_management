import datetime

from django.contrib.auth.models import User
from django.forms import ModelForm, DateInput, Form, CharField, IntegerField, Textarea, DateField, ChoiceField, \
    ModelChoiceField, HiddenInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Button, HTML
from multiupload.fields import MultiFileField
from complaints.models import Complaint, Attachment, Category


class DateInput(DateInput):
    input_type = 'date'


class ComplaintForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ComplaintForm, self).__init__(*args, **kwargs)

        self.fields['date_of_receipt'].label = "Date of Receipt in %s" % (self.user.username.replace('_', ' ').upper(),)
        self.fields['mis_register_sno'].label = "%s Dak Register S.No" % (self.user.username.replace('_', ' ').upper(),)

        self.helper = FormHelper
        self.helper.form_class = ''
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Div(
                Div('date_of_receipt', css_class='col-md-4'),
                Div('mis_register_sno', css_class='col-md-4'),
                Div('category', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('petition_id_no', css_class='col-md-4'),
                Div('id_date', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('vip_name', css_class='col-md-4'),
                Div('vip_appointment', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('subject', css_class='col-md-4'),
                Div('remarks', css_class='col-md-4'),
                Div('fwd_to', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div('petitioner_name', css_class='col-md-4'),
                Div('petition_date', css_class='col-md-4'),
                Div('files', css_class='col-md-4'),
                css_class='row'
            ),
            Div(
                Div(
                    Submit('submit', 'Submit'), css_class='text-center'
                ),
                css_class='row'
            )

        )

    class Meta:
        model = Complaint
        fields = (
            'date_of_receipt', 'mis_register_sno', 'category', 'petition_id_no', 'id_date', 'vip_name',
            'vip_appointment',
            'subject', 'remarks', 'fwd_to', 'petitioner_name', 'petition_date')
        widgets = {
            'date_of_receipt': DateInput(),
            'id_date': DateInput(),
            'petition_date': DateInput()
        }

    files = MultiFileField(min_num=1, max_num=3, max_file_size=1024 * 1024 * 5)

    def save(self, commit=True):
        instance = super(ComplaintForm, self).save(commit)
        for each in self.cleaned_data['files']:
            Attachment.objects.create(file=each, complaint=instance)
        return instance


class SearchReturnedComplaintForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SearchReturnedComplaintForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'GET'
        self.helper.form_class = ''
        self.helper.layout = Layout(
            Div(
                Div('petition_id_no', css_class='col-md-3'),
                Div('id_date', css_class='col-md-3'),
                Div('category', css_class='col-md-3'),
                Div('fwd_to', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div(
                    Submit('submit', 'Submit'), css_class='text-center'
                ),
                css_class='row'
            )

        )

    class Meta:
        model = Complaint
        fields = ('petition_id_no', 'id_date', 'category', 'fwd_to')
        widgets = {
            'id_date': DateInput(attrs={'class': 'datepicker'}),
        }


class SearchSettledComplaintForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SearchSettledComplaintForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'GET'
        self.helper.form_class = ''
        self.helper.layout = Layout(
            Div(
                Div('petition_id_no', css_class='col-md-3'),
                Div('id_date', css_class='col-md-3'),
                Div('reply_letter_no', css_class='col-md-3'),
                Div('fwd_to', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div(
                    Submit('submit', 'Submit'), css_class='text-center'
                ),
                css_class='row'
            )

        )

    class Meta:
        model = Complaint
        fields = ('petition_id_no', 'id_date', 'reply_letter_no', 'fwd_to')
        widgets = {
            'reply_letter_no': Textarea(attrs={'rows': 1}),
            'id_date': DateInput(attrs={'class': 'datepicker'}),
        }


class SearchPendingComplaintForm(Form):
    def __init__(self, *args, **kwargs):
        super(SearchPendingComplaintForm, self).__init__(*args, **kwargs)
        user_list = ((row['id'], row['username']) for row in User.objects.filter().values('id', 'username'))
        self.fields['pending_since'].choices = user_list
        self.helper = FormHelper
        self.helper.form_method = 'GET'
        self.helper.form_class = ''
        self.helper.layout = Layout(
            Div(
                Div('petition_id_no', css_class='col-md-3'),
                Div('id_date', css_class='col-md-3'),
                Div('pending_since', css_class='col-md-3'),
                Div('fwd_to', css_class='col-md-3'),
                css_class='row'
            ),
            Div(
                Div(
                    Submit('submit', 'Submit'), css_class='text-center'
                ),
                css_class='row'
            )

        )

    petition_id_no = CharField(required=False)
    id_date = DateField(required=False, widget=DateInput)
    pending_since = DateField(required=False, widget=DateInput)
    fwd_to = ModelChoiceField(required=False, queryset=User.objects.filter(groups__name='Others'))


class ComplaintUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ComplaintUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'POST'
        # self.helper.form_class = 'form-inline form-multiline'
        self.helper.layout = Layout(
            # Div(
            #     Div('status', css_class='col-md-2'),
            #     Div('reply_letter_no', css_class='col-md-2'),
            #     Div('reply_letter', css_class='col-md-2'),
            #     Div(
            #         Submit('submit','Submit'),css_class='call-md-2'
            #     ),
            #     css_class = 'row'
            # )
            Div(
                Div('status', css_class='col-md-2'),
                Div('reply_letter_no', css_class='col-md-2 col-md-offset-1'),
                Div('reply_letter', css_class='col-md-2 col-md-offset-1'),
                css_class='row'
            ),
            Div(
                Div(Submit('submit', 'Submit'), css_class='col-md-1 col-md-offset-5'),
                Div(HTML("""<a class="btn btn-default" href="{{ back_url }}">Go Back</a>"""),
                    css_class='col-md-1'),
                css_class='row'
            )
        )

    class Meta:
        model = Complaint
        fields = ('reply_letter_no', 'reply_letter', 'status')

    def save(self, commit=True):
        entry = super(ComplaintUpdateForm, self).save(commit=False)
        if entry.status == 1:
            entry.date_of_reply = datetime.date.today()
            entry.returned_date = None
        elif entry.status == 2:
            entry.returned_date = datetime.date.today()
            entry.date_of_reply = None
        if commit:
            entry.save()
        return entry


class ReplyLetterUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReplyLetterUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'POST'
        # self.helper.form_class = 'form-inline form-multiline'
        self.helper.layout = Layout(
            # Div(
            #     Div('status', css_class='col-md-2'),
            #     Div('reply_letter_no', css_class='col-md-2'),
            #     Div('reply_letter', css_class='col-md-2'),
            #     Div(
            #         Submit('submit','Submit'),css_class='call-md-2'
            #     ),
            #     css_class = 'row'
            # )
            Div(
                Div('status', css_class='col-md-2'),
                Div('reply_letter_no', css_class='col-md-2 col-md-offset-1'),
                Div('reply_letter', css_class='col-md-2 col-md-offset-1'),
                css_class='row'
            ),
            Div(
                Div(Submit('submit', 'Submit'), css_class='col-md-1 col-md-offset-5'),
                Div(HTML(
                    """<a class="btn btn-default" href="{% url 'settled-complaints'  complaint.category %}">Go Back</a>"""),
                    css_class='col-md-1'),
                css_class='row'
            )
        )

    class Meta:
        model = Complaint
        fields = ('reply_letter_no', 'reply_letter', 'status')

    def save(self, commit=True):
        entry = super(ComplaintUpdateForm, self).save(commit=False)
        if entry.status == 1:
            entry.date_of_reply = datetime.date.today()
            entry.returned_date = None
        elif entry.status == 2:
            entry.returned_date = datetime.date.today()
            entry.date_of_reply = None
        if commit:
            entry.save()
        return entry


class ReturnedUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReturnedUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'POST'
        # self.helper.form_class = 'form-inline form-multiline'
        self.helper.layout = Layout(
            # Div(
            #     Div('status', css_class='col-md-2'),
            #     Div('reply_letter_no', css_class='col-md-2'),
            #     Div('reply_letter', css_class='col-md-2'),
            #     Div(
            #         Submit('submit','Submit'),css_class='call-md-2'
            #     ),
            #     css_class = 'row'
            # )
            Div(
                Div('fwd_to', css_class='col-md-2'),
                # Div('reply_letter_no', css_class='col-md-2 col-md-offset-1'),
                # Div('reply_letter', css_class='col-md-2 col-md-offset-1'),
                css_class='row'
            ),
            Div(
                Div(Submit('submit', 'Submit'), css_class='col-md-1 col-md-offset-5'),
                Div(HTML("""<a class="btn btn-default" href="{% url 'returned-complaints' %}">Go Back</a>"""),
                    css_class='col-md-1'),
                css_class='row'
            )
        )

    class Meta:
        model = Complaint
        fields = ('fwd_to',)
        widgets = {'status': HiddenInput()}

    def save(self, commit=True):
        entry = super(ReturnedUpdateForm, self).save(commit=False)
        entry.status = 0
        if commit:
            entry.save()
        return entry


class SearchReportForm(Form):
    def __init__(self, *args, **kwargs):
        super(SearchReportForm, self).__init__(*args, **kwargs)
        # user_list = ((row['id'], row['username']) for row in User.objects.filter().values('id', 'username'))
        # self.fields['fwd_to'].choices = user_list

        self.helper = FormHelper
        self.helper.form_method = 'GET'
        self.helper.form_class = ''
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('start_date', css_class='col-md-4'),
                    Div('end_date', css_class='col-md-4'),
                    Div('fwd_to', css_class='col-md-4'),
                    css_class='row'
                ),
                Div(
                    Div(
                        Submit('submit', 'Submit'), css_class='text-center'
                    ),
                    css_class='row'
                ),
                css_class="container")

        )

    start_date = DateField(label="From Date", required=False, widget=DateInput)
    end_date = DateField(label="To Date", required=False, widget=DateInput)
    fwd_to = ModelChoiceField(required=False, queryset=User.objects.filter(groups__name='Others'))
