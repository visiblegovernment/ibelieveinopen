from django.shortcuts import render_to_response, get_object_or_404
from app.mainapp.models import  Signup, Politician, PoliticianPledge, Province, Pledge, PledgeOption, Riding, EmailConfirmation
from django.contrib.flatpages.models import FlatPage
from django.template import Context, RequestContext
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
import urllib, urllib2, re
from django.core.mail import EmailMessage
from django.db import connection
import time

class TotalCount:

    def __init__(self, name, count, other="" ):
        self.name = name
        self.count= count
        self.other=other

def front_page(request):
    party_cursor = connection.cursor()
    party_cursor.execute('select party, count(id) as total from politicians where ipledge_has_responded=true and ipledge_supports_none = false and reptype = "M" group by party order by count(id) desc')
    i = party_cursor.fetchone()
    parties = []
    while i:
        parties.append( TotalCount(i[0], i[1] ))
        i=party_cursor.fetchone()

    province_cursor = connection.cursor()
    province_cursor.execute('select mainapp_riding.province, count(signups.id) as total from signups join mainapp_riding on signups.riding_id = mainapp_riding.edid where signups.verified = true group by mainapp_riding.province order by count(signups.id) DESC limit 8')
    provinces = []
    i = province_cursor.fetchone()
    while i:
        province = Province()
        province.abbrev = i[0]
        provinces.append( TotalCount( province.fullname(), i[1]) )
        i = province_cursor.fetchone()

    riding_cursor = connection.cursor()
    riding_cursor.execute('select  mainapp_riding.name, mainapp_riding.edid, count(signups.id) as total from signups  join mainapp_riding on signups.riding_id = mainapp_riding.edid  where signups.verified = true  group by signups.riding_id order by count(signups.id) DESC limit 12')

    i=riding_cursor.fetchone()
    ridings = []
    while i:
        province = Province()
        name = i[0] + ", " +  province.from_edid(i[1])
        ridings.append( TotalCount( name , i[2], i[1] ) )
        i=riding_cursor.fetchone()
    received_candidate_pledge = (len(parties) != 0)

    today=time.time()
    ten_days_ago = time.strftime("%Y-%m-%d", time.localtime(today-24*60*60*10))

    return render_to_response("front_page.html",
        {"page": "home",
         "parties": parties,
         "provinces" : provinces,
         "ridings": ridings,
         'recent_voter_pledges' : Signup.objects.order_by("-created_at").filter(verified=True, created_at__gte=ten_days_ago)[0:15],
         "voter_total": Signup.objects.filter( verified=True ).count(),
         "candidate_total": Politician.objects.filter( ipledge_has_responded = True, reptype="M" ).count(),
         "received_candidate_pledge" : received_candidate_pledge,
         'recent_cand_pledges' : Politician.objects.order_by("-created_at").filter(reptype="M",ipledge_has_responded=True)[0:5],
         "excerpt":True},
         context_instance=RequestContext(request))


def pledge(request):
    return HttpResponseRedirect("/pledge/citizen/")


def citizens_pledge(request):
    pledges = Pledge.objects.all()
    for pledge in pledges:
        pledge.change_tense()
        pledge.translate()

    return render_to_response("join/citizens_pledge.html",
    {"page": "pledge",
    "pledges":pledges},
    context_instance=RequestContext(request))

def candidates_pledge(request):
    pledges = Pledge.objects.all()
    return render_to_response("candidate_pledge.html",
        {"page": "pledge", "pledges":pledges},
        context_instance=RequestContext(request))

def candidates_pledge_info(request, id):
    politician = get_object_or_404(Politician, id=id)
    pledges = Pledge.objects.all()
    for pledge in pledges:
        pledge.change_tense()
    return render_to_response("ipledge/view_pledge.html",
    {"page":"results", "politician":politician, "pledges":pledges},
    context_instance=RequestContext(request))

def about(request):
    return render_to_response("about.html",
        {"page": "about"},
        context_instance=RequestContext(request))

def privacy(request):
    return render_to_response("privacy.html",
        {"page": "about/privacy"},
        context_instance=RequestContext(request))

def tos(request):
    return render_to_response("tos.html", {"page": "about/tos"}, context_instance=RequestContext(request))

def resources(request):
     return render_to_response("resources.html", {"page":"home"},
                               context_instance=RequestContext(request))

