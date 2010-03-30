from django.contrib import admin
from models import Signup, Pledge, PledgeOption, Politician,\
 Politician


class SignupAdmin(admin.ModelAdmin):
    list_display = ('email', 'postalcode')
    list_filter = ('created_at', )
    search_fields = ['email', 'postalcode']
#admin.site.register(Signup, SignupAdmin)

class PledgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    list_filter = ('created_at', )
    search_fields = ['name', 'pledge_text', 'description']
#admin.site.register(Pledge, PledgeAdmin)

class PledgeOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'pledge')
    list_filter = ('option_type',)
    search_fields = ['name', 'text']
admin.site.register(PledgeOption, PledgeOptionAdmin)


class PoliticianAdmin(admin.ModelAdmin):
    list_display = ('fname', 'lname', 'email', 'website', 'pic', 'province' )
    list_filter = ('party', 'province', 'party')
    search_fields = ('fname', 'lname')
admin.site.register(Politician, PoliticianAdmin)

