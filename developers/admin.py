from django.contrib import admin
from .models import Developer
from .models import Event
from .models import TemporalPredictor

def standard_fields(model):
    fields = []
    for field in model._meta.fields:
        if field.get_internal_type() != "ManyToManyField":
            fields.append(field.name)
    return tuple(fields)

class DeveloperAdmin(admin.ModelAdmin):
    list_display = standard_fields(Developer)
    list_display_links = list_display
    search_fields = ['login', 'gh_id']
    list_filter = ['gh_type', 'site_admin', 'hireable']
admin.site.register(Developer, DeveloperAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = standard_fields(Event)
    list_display_links = list_display
    search_fields = ['gh_type', 'actor_login', 'gh_id', 'repo_id', 'repo_name']
    list_filter = ['gh_type']
admin.site.register(Event, EventAdmin)

class TemporalPredictorAdmin(admin.ModelAdmin):
    list_display = standard_fields(TemporalPredictor)
    list_display_links = list_display
    list_filter = ['reference', 'formula', 'statistic', 'year', 'month']
    search_fields = list_display
admin.site.register(TemporalPredictor, TemporalPredictorAdmin)
