from search_views.filters import BaseFilter


class ReturnedComplaintsFilter(BaseFilter):
    search_fields = {
        "petition_id_no": {"operator": "__exact", "fields": ["petition_id_no"]},
        "id_date": ['id_date'],
        "category": ['category__id'],
        "fwd_to": ['fwd_to__id'],
    }


class SettledComplaintsFilter(BaseFilter):
    search_fields = {
        "petition_id_no": {"operator": "__exact", "fields": ["petition_id_no"]},
        "id_date": ['id_date'],
        "reply_letter_no": ['reply_letter_no'],
        "fwd_to": ['fwd_to__id'],
    }


class PendingComplaintsFilter(BaseFilter):
    search_fields = {
        "petition_id_no": {"operator": "__exact", "fields": ["petition_id_no"]},
        "id_date": ['id_date'],
        "pending_since": {"operator": "__gte", "fields": ["id_date"]},
        "fwd_to": ['fwd_to__id'],
    }


class ReportFilter(BaseFilter):
    search_fields = {
        "start_date": {"operator": "__gte", "fields": ["id_date"]},
        "end_date": {"operator": "__lte", "fields": ["id_date"]},
        "fwd_to": ['fwd_to__id'],
    }
