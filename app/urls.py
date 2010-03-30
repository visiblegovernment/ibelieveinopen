from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns =  patterns('', #XXX add + after uncommenting admin module above
    (r'^accounts/', include('registration.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += patterns('app.mainapp.views.default',
     url(r'^pledge/candidate/info/(\d+)', 'candidates_pledge_info',  name="candidate_pledge"),
    (r'^pledge/candidate/', 'candidates_pledge'),
    (r'^pledge/citizen/', 'citizens_pledge'),
    (r'^pledge/', 'pledge'),
    (r'^about/privacy', 'privacy'),
    (r'^about/tos', 'tos'),
    (r'^about/$', 'about'),
    (r'^$', 'front_page')
)

urlpatterns += patterns('app.mainapp.views.join',
    (r'^join/submit/(\w+)/$', 'join_submit_form'),
    (r'^join/success', 'join_success'),
    (r'^join/select_riding/(\d+)/', 'select_riding'),
    (r'^join/confirm/(\w+)/$', 'confirm_email'),
    (r'^member/no_emails/(\w+)/$', 'no_emails'),
)

urlpatterns += patterns('app.mainapp.views.ipledge',
    url(r'^ipledge/([RCrc]\d{6})/$', 'ipledge_campaign',  name='ipledge_campaign'),
    url(r'^ipledge/login/(\w\d{6})/$', 'ipledge_login', name='ipledge_login'),
)

urlpatterns += patterns('app.mainapp.views.results',
    url(r'^results/party/(\w+)/$', 'show_party_index'),
    url(r'^results/postalcode/', 'lookup_postalcode'),
    url(r'^results/select_riding/(\w+)/$', 'select_riding_by_pcode'),
    url(r'^results/province/(\w+)/$', 'select_riding_by_province'),
    url(r'^results/riding/(\d+)/$', 'show_riding'),
    url(r'^results/politicians/$', 'show_campaign_summary'),
    url(r'^results/summary/$', 'show_campaign_summary'),
    url(r'^results/summary/(\w+)/(\d+)/$', 'show_yes_or_no'),
)

#The following is used to serve up local media files like images
if settings.LOCAL_DEV:
    baseurlregex = r'^media/(?P<path>.*)$'
    urlpatterns += patterns('',
        (baseurlregex, 'django.views.static.serve',
        {'document_root':  settings.MEDIA_ROOT}),
    )
