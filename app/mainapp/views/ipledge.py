from django.template import Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import urllib, urllib2, re
import time
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login
from app.mainapp.models import  Pledge, \
    Politician, PoliticianPledge, \
    PledgeOption
from django.utils.translation import ugettext


def get_polid(pid):
    polid =   int(pid[1:]) - 2000 #XXX: All ids are offset by 2000
    return polid

def ipledge_campaign(request, pid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('ipledge_login', args=[pid]))
    pid = pid.lower()
    pledges = Pledge.objects.all()
    politician_id = get_polid(pid)
    if request.user.username != pid:
        return render_to_response("ipledge/pledge.html",
            {"page":"pledge",
            "msg":"Permission denied.",
            "pledges":pledges}, context_instance=RequestContext(request))

    try:
        politician = Politician.objects.filter(id=politician_id)[0]
    except:
        return render_to_response("ipledge/pledge.html",
                {"page":"pledge",
                "msg":"Sorry. we don't have the record you are looking for",
                "pledges":pledges}, context_instance=RequestContext(request))


    if request.method == 'POST':
        # Verify pledge selection
        none_supported = request.POST.has_key('no')
        ps = []
        for pledge in pledges:
            if request.POST.has_key(pledge.code):
                ps.append(pledge)

        if ( (none_supported == False) and (len(ps) == 0)):
            return render_to_response("ipledge/pledge.html",
                {"page":"pledge",
                "msg":"You must select at least one pledge, or select 'none'.",
                "pledges":pledges}, context_instance=RequestContext(request))

        if ((len(ps) > 0) and (none_supported == True)):
            return render_to_response("ipledge/pledge.html",
                {"page":"pledge",
                "msg":"Please check your reponse. You have chosen to support some issues as well 'support none'.",
                'politician':politician,
                "pledges":pledges,
                }, context_instance=RequestContext(request))

        pledge_options = []
        for po in PledgeOption.objects.all():
            if request.POST.has_key( po.html_id ) and po.option_type == PledgeOption.CANDIDATE_OPTION:
                pledge_options.append( po )

        politician.ipledge_support_none = none_supported
        politician.save_pledges( request.POST )

        return render_to_response('ipledge/embed.html',
            {"page":"pledge",
            'politician': politician,
            },
            context_instance=RequestContext(request))


    else: #GET
        return render_to_response('ipledge/pledge.html',
            {'page':'pledge',
            'politician': politician,
            'pledges':pledges},
            context_instance=RequestContext(request))

def ipledge_login(request, pid):
    if request.method == 'GET':
        try:
            polid = get_polid(pid)
            politician = Politician.objects.get(id=polid)
            return render_to_response('ipledge/login.html',
                {'page':'pledge',
                'politician':politician,
                'pid':pid},context_instance=RequestContext(request))
        except Exception, e:
            return render_to_response('error.html',
                {"page":"pledge",
                "message":"Sorry. we don't have the record (%s) you are looking for" % (pid, )},
                context_instance=RequestContext(request))

    elif request.method =='POST':
        password = request.POST.get('password', '')
        user = authenticate(username=pid, password=password)
        if user is not None:
            #XXX: also add handler for disabled accounts. is_active.
            login(request, user)
            return HttpResponseRedirect(reverse('ipledge_campaign', args=[pid]))
        else:
            return HttpResponseRedirect(reverse('ipledge_login', args=[pid]))

