from django.template import Context, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.db import connection
from app.mainapp.models import  Signup, Pledge, Riding, Politician, PoliticianPledge, Province, PledgeOption, PostalCode, VoterPledgeTotal,VoterPledgeTotals, PoliticianPledgeTotals

import re

def show_party_index(request, party):
    #default is liberal
    candidates = Politician.objects.filter(party=party, reptype="M").order_by('province')
    return render_to_response('results/politician_index.html',
        {'page':'results',
         'subnav': "All Members",
         'sub-subnav': party,
         'candidates':candidates,
        },
        context_instance=RequestContext(request))

def show_yes_or_no(request,yes_or_no_str,pledge_id):
    if (yes_or_no_str == 'Yes'):
        yes_or_no = True
    else:
        yes_or_no = False
    pledge = get_object_or_404(Pledge, id=pledge_id)
    pledge.change_tense()
    pledge.translate()
    candidates = Politician.objects.filter(reptype='M', politicianpledge__supports = yes_or_no, politicianpledge__pledge = pledge)
    comments = PoliticianPledge.objects.filter(supports=yes_or_no, pledge = pledge, politician__reptype='M' ).exclude(comments = "")

    return render_to_response('results/pledge_yes_or_no.html',
        {'page':'results',
         'subnav': "Summary",
         'response':yes_or_no_str,
         'pledge':pledge,
         'comments':comments,
         'candidates':candidates,
        },
        context_instance=RequestContext(request))

def combine_results( pledges, parties, politicians_totals, citizens_totals ):
    politicians_results = politicians_totals.results()
    citizens_results = citizens_totals.results()

    for i in range(0,len(pledges)):
        politicians_results[i].yes_responses.append( citizens_results[i].yes_total )
        politicians_results[i].no_responses.append( citizens_results[i].no_total )

    # add 'voters' to parties list
    parties.append('Voters')
    return( politicians_results )


def show_riding(request,edid):
    riding = get_object_or_404(Riding, edid=edid)
    pledges = Pledge.objects.all()

    try:
        mp = Politician.objects.get( riding_id = riding, reptype = "M" )
        party = mp.party
    except:
        party = "Ind."

    parties = [party]

    politicians_totals = PoliticianPledgeTotals( pledges, parties )
    politicians_totals.set_riding( riding )
    citizens_totals = VoterPledgeTotals( pledges )
    citizens_totals.set_riding(riding)

    all_results = combine_results(pledges,parties,politicians_totals, citizens_totals )

    candidates = Politician.objects.filter(riding_id=riding, reptype='M')
    return render_to_response('results/riding.html',
        {'page':'results',
         'subnav': 'By Riding',
         'parties': parties,
         'candidates':candidates,
         'riding':riding,
         'politician_results' : all_results,
        }, context_instance=RequestContext(request))

def lookup_postalcode(request):
    if request.method == "POST":
        postalcode = request.POST["postalcode"].upper()
        postalcode = re.sub("\s+", "", postalcode)
        if( postalcode == "" ):
            msg = "Enter a valid postal code."
            return render_to_response("results/lookup_postalcode.html", {"msg":msg, "page":"results",'subnav':'Riding'}, context_instance=RequestContext(request))
        try:
            print "getting " + postalcode
            postalcodeobj = PostalCode.objects.get(code =  postalcode )
            return HttpResponseRedirect("/results/riding/" + str(postalcodeobj.riding.edid) + "/" )
        except:
            return HttpResponseRedirect("/results/select_riding/" + postalcode +"/" )
    else:
        provinceobj = Province()
        provinces = provinceobj.abbrev_lookup.keys()
        print provinces
        return render_to_response('results/lookup_postalcode.html',
            {'page':'results',
            'subnav': 'By Riding',
            'provinces':  sorted( provinces ) }, context_instance=RequestContext(request))

def select_riding_by_pcode(request,postalcode):
    pcodeobj = PostalCode(code=postalcode)
    return render_to_response('results/select_riding_by_pcode.html',
        {'page':'results',
         'subnav': "By Riding",
         'ridings': pcodeobj.get_ridings(),
        },context_instance=RequestContext(request))

def select_riding_by_province( request, province ):
    ridings =	Riding.objects.filter(province=province)
    return render_to_response('results/select_riding_by_province.html',
        {'page':'results',
         'subnav': "By Riding",
         'ridings': ridings,
        },context_instance=RequestContext(request))

def show_campaign_summary(request):

    pledges = Pledge.objects.all()
    parties = ['Bloc','Conservative','Liberal','NDP']
    politicians_totals = PoliticianPledgeTotals( pledges, parties )

    citizens_totals = VoterPledgeTotals( pledges )
    all_results = combine_results(pledges,parties,politicians_totals, citizens_totals )


    parties[1] = 'Cons.'
    return render_to_response('results/campaign_summary.html',
        {'page':'results',
         'subnav': "Summary",
         'politician_results' : all_results,
         'parties':parties,
        },context_instance=RequestContext(request))

