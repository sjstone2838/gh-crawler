from django.contrib import admin
from .models import Developer
from .models import Event

def standard_fields(model):
    fields = []
    for field in model._meta.fields:
        if field.get_internal_type() != "ManyToManyField":
            fields.append(field.name)
    return tuple(fields)

class DeveloperAdmin(admin.ModelAdmin):
    list_display = standard_fields(Developer)
    list_display_links = list_display
admin.site.register(Developer, DeveloperAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = standard_fields(Event)
    list_display_links = list_display
admin.site.register(Event, EventAdmin)
