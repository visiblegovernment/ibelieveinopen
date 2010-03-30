from django.shortcuts import render_to_response, get_object_or_404
from app.mainapp.models import Signup, Politician, VoterPledge, PoliticianPledge, Pledge, PledgeOption, IBelieveEmail, Province, PostalCode, Riding, EmailConfirmation
from django.template import Context, RequestContext
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
import urllib, urllib2, re
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db import connection
import time

def join_submit_form(request, xml):
    if request.method == "POST":

        #postal code is validated in javascript
        postalcode = request.POST["postalcode"]
        postalcode = re.sub("\s+", "", postalcode)
        postalcode=postalcode.upper()

        try:
            signup, created = Signup.objects.get_or_create(email=request.POST["email"])
            signup.verified = False
            signup.name = request.POST["name"]
            signup.postalcode=postalcode
            signup.ipaddr=request.META.get('REMOTE_ADDR')
            signup.save()
            signup.save_pledges(request.POST)

            if PostalCode.objects.filter(code=postalcode).count() != 0:
              pcode_obj = PostalCode.objects.get(code=postalcode)
              signup.set_riding(pcode_obj.riding)
              signup.send_confirmation_email()
              return HttpResponseRedirect("/join/success.html" )
            else:
              return HttpResponseRedirect("/join/select_riding/" + str(signup.id) + "/")

        except Exception, e:
            print '%'*78
            print e
            msg = "There was an error - please try again."
            return render_to_response("join/citizens_pledge.html", {"msg":msg, "page":"pledge"}, context_instance=RequestContext(request))

    else:
        return HttpResponseRedirect('/')

def join_success(request):
  return render_to_response('join/success.html',
                              {'page':'pledge'
                              }, context_instance=RequestContext(request))


def select_riding(request, voter_id):
  voter = get_object_or_404(Signup, id=voter_id)

  if request.method == "POST":
    riding = get_object_or_404(Riding, edid = request.POST["edid"])
    voter.set_riding(riding)
    voter.send_confirmation_email()
    return HttpResponseRedirect("/join/success.html" )
  else:
    postalcode = PostalCode(code = voter.postalcode )
    ridings = postalcode.get_ridings()
    return render_to_response('join/select_riding.html',
                              {'page':'pledge', 'voter':voter,'ridings':ridings
                              }, context_instance=RequestContext(request))

def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    member = EmailConfirmation.objects.confirm_email(confirmation_key)
    if( (member != None) and (member.riding_id)):
        pcode,create = PostalCode.objects.get_or_create( code = member.postalcode,
                              riding = member.riding )
    #send a thankyou email
    email = IBelieveEmail("spreadtheword")
    email.send(member.email)

    return render_to_response('join/confirmed.html',
                              {'page':'pledge',
                              'member': member
                              }, context_instance=RequestContext(request))


def no_emails(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    key = get_object_or_404(EmailConfirmation, confirmation_key = confirmation_key)
    voter = key.email_address

    if voter :
        voter.no_emails = True
        voter.save()

    return render_to_response('join/no_email.html',
                              {'page':'pledge',
                              'member': voter
                              }, context_instance=RequestContext(request))


