from __future__ import unicode_literals

import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)
    clean_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category



class Complaint(models.Model):
    CATEGORY = (("COAS", "COAS"), ("MOD", "MOD"), ("MODPMO", "MOD/PMO"), ("MP", "MP"), ("RMP", "RMP"), ("VIP", "VIP"))
    COMPLAINT_STATUS = ((0, "PENDING"), (1, "CLEARED"), (2, "RETURNED"))

    date_of_receipt = models.DateField("Date of Receipt in MIS")
    mis_register_sno = models.CharField("MIS Dak Register S.No", max_length=50)
    # category = models.CharField(max_length=100,choices=CATEGORY)
    category = models.ForeignKey(Category)
    petition_id_no = models.CharField("Petition ID No", max_length=200)
    status = models.IntegerField(default=0, choices=COMPLAINT_STATUS)
    id_date = models.DateField()
    vip_name = models.CharField("Name of MP/VIP", max_length=200, blank=True)
    vip_appointment = models.CharField("Appointment of MP/ VIP", max_length=200, blank=True)
    subject = models.TextField()
    remarks = models.TextField(max_length=200, blank=True)
    fwd_to = models.ForeignKey(User, limit_choices_to={'groups__name': u'Others'})
    fwd_date = models.DateField(auto_now_add=True)
    petitioner_name = models.TextField("Name of Petitioner", blank=True)
    petition_date = models.DateField(null=True)
    reply_letter_no = models.TextField("Reply Letter No", blank=True)
    date_of_reply = models.DateField(null=True)
    reply_letter = models.FileField(upload_to='uploads/%Y/%m/%d/reply-letters', blank=True)
    returned_date = models.DateField(null=True)

    class Meta:
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def __str__(self):
        return self.petition_id_no

    def get_absolute_url(self):
        return reverse('add-complaint')

    @property
    def pending_since(self):
        days_past = (datetime.date.today() - self.id_date).days
        if days_past > 730:
            pending_since = "25 Months & Above"
        elif days_past > 365:
            pending_since = "12-24 Months"
        elif days_past > 180:
            pending_since = "07-12 Months"
        elif days_past > 90:
            pending_since = "04-06 Months"
        else:
            pending_since = "0-03 Months"
        return pending_since

    @property
    def days_past(self):
        days_past = (datetime.date.today() - self.id_date).days
        return days_past


class Attachment(models.Model):
    complaint = models.ForeignKey(Complaint, verbose_name='Complaint')
    file = models.FileField('Attachment', upload_to='uploads/%Y/%m/%d/complaint-files/')
