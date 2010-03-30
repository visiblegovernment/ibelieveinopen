from django.db import models
from datetime import datetime, timedelta
from random import random
import sha
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import models, IntegrityError
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.admin.models import User
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib, re
from django.db import connection
import time

REPTYPE = (
('X','Candidate'),
('M','Member of Parliament'))


PARTIES =  { 'Liberal': "0",
             'Conservative': "1",
             'NDP':"2",
             'Green': "3",
             'Bloc': "4" }


def is_live_url(url):
    req = Request(url)
    try:
        urlopen(req)
    except HTTPError, e:
        return False
    return True

class IBelieveUrl(object):

    def __init__(self, abs_url):
        self.abs_url = abs_url

    def __unicode__(self):
        return("http://" + settings.SITE_ROOT + self.abs_url)

class Province(object):

    edid_lookup = { '48':'AB','59':'BC','46':'MB','13':'NB','10':'NL','61':'NT','12':'NS','62':'NU','35':'ON','11':'PE','24':'QC','47':'SK','60':'YT'}
    abbrev_lookup = { 'AB':'Alberta','BC':'British Columbia','MB':'Manitoba','NB':'New Brunswick','NL':'Newfoundland','NT':'NWT','NS':'Nova Scotia','NU':'Nunavut','ON':'Ontario','PE':'PEI','QC':'Quebec','SK':'Saskatchewan','YT':'Yukon'}

    abbrev = "AB"

    def from_edid( self, edid ):
        edidstr = str(edid)

        for i in self.edid_lookup.keys():
            if( edidstr.find(i) == 0):
                self.abbrev = self.edid_lookup[i]
                return(self.abbrev_lookup[self.abbrev])
        return("no province found for " + edidstr)

    def fullname(self):
        return( self.abbrev_lookup[self.abbrev] )

    def from_abbrev(self, abbrev):
        self.abbrev = abbrev
        return( self.abbrev_lookup(self.abbrev) )


class Riding(models.Model):
    edid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80,unique=True)
    province = models.CharField(max_length=3)
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
       return '/results/riding/%s/' % (str(self.edid), )


class PostalCode(models.Model):
    code = models.CharField(max_length=7,primary_key=True)
    riding = models.ForeignKey(Riding,null=True)

    lookup = { 'A' : ['NL'],
            'M' : ['ON'],
            'B' : ['NS'],
            'N' : ['ON'],
            'C' : ['PE'],
            'P' : ['ON'],
            'E' : ['NB'],
            'R' : ['MB'],
            'G' : ['QC'],
            'S' : ['SK'],
            'H' : ['QC'],
            'T' : ['AB'],
            'J' : ['QC'],
            'V' : ['BC'],
            'K' : ['ON'],
            'X' : ['NU','NT'],
            'L' : ['ON']
            }

    def get_ridings(self):
        provinces = self.lookup[ self.code[0] ]
        ridings =	Riding.objects.filter(province__in=provinces)
        return( ridings )

    def __unicode__(self):
        return self.code


class Signup(models.Model):
    email = models.CharField(max_length=50)
    name = models.CharField(max_length=40)
    postalcode = models.CharField(max_length=7)
    riding = models.ForeignKey(Riding,null=True)
    province = models.CharField(max_length=2,blank=True, null=True)
    ipaddr = models.CharField(max_length=90, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    email_sent=models.BooleanField(default=False)
    no_emails = models.NullBooleanField(default=False, null=True)

    def ipledge_supported_issues(self):
        return VoterPledge.objects.filter(signup=self, supports=True).count()

    def set_riding(self, riding):
        self.riding =  riding
        self.province = riding.province
        self.save()

    def send_confirmation_email(self):
        self.email_sent = EmailConfirmation.objects.send_confirmation(self)
        self.save()

    def save_pledges(self, pledge_map):
        pledges = Pledge.objects.all()
        for pledge in pledges:
            supports = pledge_map.has_key(pledge.code)
            newpledge,created = VoterPledge.objects.get_or_create(
                signup=self,
                pledge=pledge
            )

            newpledge.supports=supports
            newpledge.created_at=time.strftime("%Y-%m-%d %H:%M:%S")
            newpledge.save()

    def get_no_emails_absolute_url(self):
            emailconf = EmailConfirmation.objects.filter( email_address = self )[0]
            return("/member/no_emails/" + emailconf.confirmation_key )

    def __unicode__(self):
        return '%s/%s ' % (self.email, self.postalcode)

    class Meta:
        db_table = u'signups'


class Pledge(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    pledge_text = models.CharField(max_length=300)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    def change_tense_of_field( self, text ):
        p = re.compile(r' I ')
        text = p.sub(' the MP ', text)
        p = re.compile(r' my ')
        text= p.sub(' his or her ', text)
        p = re.compile(r' am ')
        text= p.sub(' is ', text)
        return( text )

    def change_tense( self ):
        self.description = self.change_tense_of_field( self.description )
        self.pledge_text = self.change_tense_of_field( self.pledge_text )

    def translate( self ):
        self.description = _( self.description )
        self.pledge_text = _( self.pledge_text)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'pledges'


class PledgeOption( models.Model ):
    CITIZEN_OPTION = 'citizen'
    CANDIDATE_OPTION = 'candidate'
    PLEDGE_OPTION_CHOICES = ( (CITIZEN_OPTION,'Citizen'),(CANDIDATE_OPTION,'Candidate') )

    name = models.CharField( max_length=100 )
    text = models.CharField( max_length=100 )
    pledge = models.ForeignKey( Pledge )
    form_html = models.TextField()
    info_html = models.TextField()
    html_id = models.CharField( max_length=25 )
    option_type = models.CharField( max_length=10, choices=PLEDGE_OPTION_CHOICES, default='citizen' )

    def __unicode__( self ):
        return self.name



class Politician(models.Model):
    POL_PARTIES = (
        ('Liberal', 'Liberal'),
        ('Conservative', 'Conservative'),
        ('NDP', 'NPD'),
        ('Green', 'Green'),
    )

    fname = models.CharField(max_length=100)
    mname = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100)
    province = models.CharField(max_length=2,blank=True, null=True)
    riding_id = models.ForeignKey(Riding, db_column='riding_id')
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=20,blank=True, null=True)
    phone = models.CharField(max_length=20,blank=True, null=True)
    website =  models.URLField(blank=True, null=True)
    pic = models.URLField(blank=True, null=True)
    party = models.CharField(max_length=20, blank=True, null=True, choices=POL_PARTIES)
    created_at = models.DateTimeField(auto_now_add=True)
    donateurl = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    reptype = models.CharField(max_length=1,blank=True, null=True)
    ipledge_email_sent = models.BooleanField(default=False)
    ipledge_has_responded = models.BooleanField(default=False)
    ipledge_supports_none = models.BooleanField(default=False)
    ipledge_nag_count = models.IntegerField(default=0)
    ipledge_voters_notified_of_pledge = models.BooleanField(default=False)
    class Meta:
        db_table = u'politicians'

    def __unicode__(self):
        return '%s %s %s' % (self.fname, self.mname, self.lname)

    def get_absolute_url(self):
        return '/pledge/candidate/info/%s/' % (self.id, )

    def get_pledge(self, pledge):
        #XXX: check for side effects of this;
        try:
            return PoliticianPledge.objects.get(politician=self, pledge=pledge)
        except:
            return None

    def save_pledges(self, data ):
        self.ipledge_has_responded = True
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.save()

        pledges = Pledge.objects.all()
        for pledge in pledges:
            comments = data.get('comment-%s' % (pledge.code,), '')
            supports = data.has_key(pledge.code)
            newpledge,created = PoliticianPledge.objects.get_or_create(
                politician=self,
                pledge=pledge,
                )
            newpledge.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
            newpledge.comments= comments
            newpledge.supports = supports
            newpledge.save()

    def pic_url(self):
        url = None
        if self.pic:
            url = self.pic
        return url

    def name(self):
        return '%s %s' % (self.fname, self.lname)

    def ipledge_supported_issues(self):
        return len(self.politicianpledge_set.filter(supports__exact=True))


class VoterPledge(models.Model):
    signup = models.ForeignKey(Signup)
    pledge = models.ForeignKey(Pledge)
    supports = models.NullBooleanField(blank=True, null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u'voter_pledges'

class PoliticianPledge(models.Model):
    politician = models.ForeignKey(Politician)
    pledge = models.ForeignKey(Pledge)
    supports = models.NullBooleanField(blank=True, null=True, default=False)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'politicians_pledges'


class PartyPledge( models.Model ):
    party = models.CharField(max_length=20)
    pledge_id = models.ForeignKey(Pledge)
    supports = models.NullBooleanField(blank=True, null=True, default=False)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'party_pledges'

class Issue(models.Model):
    name = models.CharField(max_length=80)
    desc = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'track_issue'




class EmailConfirmationManager(models.Manager):

    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.save()
            return email_address

    def create_confirmation_key(self,signup):
        salt = sha.new(str(random())).hexdigest()[:5]
        confirmation_key = sha.new(salt + signup.email ).hexdigest()
        self.create(email_address=signup, sent=datetime.now(), confirmation_key=confirmation_key)

        return( confirmation_key )

    def send_confirmation(self, signup):
        try:
            email = ConfirmationEmailTemplate( self.create_confirmation_key(signup) )
            return email.send(signup.email)
        except Exception, e:
            print '%'*78
            print e
            return False

    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmate.delete()


class EmailConfirmation(models.Model):
    email_address = models.ForeignKey(Signup)
    sent = models.DateTimeField()
    confirmation_key = models.CharField(max_length=40)

    objects = EmailConfirmationManager()

    def key_expired(self):
        expiration_date = self.sent + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return expiration_date <= datetime.now()
        key_expired.boolean = True

    def __unicode__(self):
        return u"confirmation for %s" % self.email_address

    class Meta:
        db_table = 'volemlconfirm'

class VoterPledgeTotal:

    def __init__(self, pledge, yes_total, no_total ):
        self.id = id
        self.pledge = pledge
        self.yes_total = yes_total
        self.no_total = no_total

class VoterPledgeTotals:

    def __init__( self, pledges, where = ""  ):
        self.where = where
        self.pledges = pledges

    def results(self):
        yes_responses = self.get_voter_response_hash('true',self.where)
        no_responses = self.get_voter_response_hash('false',self.where)
        results = []
        for pledge in self.pledges:
            yes_total = '-'
            no_total = '-'
            if( yes_responses.has_key( pledge.id )):
                yes_total = yes_responses[ pledge.id ]
            if( no_responses.has_key( pledge.id )):
                no_total = no_responses[ pledge.id ]
            results.append( VoterPledgeTotal( pledge, yes_total, no_total ) )
        return( results )

    def set_riding( self, riding):
        self.where = " signups.riding_id =" + str( riding.edid )

    def get_voter_response_hash(self,supports, where):
        query = "select voter_pledges.pledge_id, count( voter_pledges.supports ) from signups join voter_pledges on voter_pledges.signup_id = signups.id where signups.verified = true and voter_pledges.supports = " + supports
        if( self.where != "" ):
            query += " and "
            query += self.where
        query += " group by voter_pledges.pledge_id"

        cursor = connection.cursor()
        cursor.execute(query)
        i = cursor.fetchone()

        hash = {}
        while i:
            pledge_id, total = i[0],i[1]
            hash[ int(pledge_id) ] = total
            i=cursor.fetchone()
        return( hash )


class PoliticianPledgeTotal:

    def __init__(self, id, pledge ):
        self.id = id
        self.pledge = pledge
        self.pledge.change_tense()
        self.pledge.translate()
        self.comments = []
        self.yes_responses = []
        self.no_responses = []

class PoliticianPledgeTotals:

    def __init__( self, pledges, parties,where="" ):
        self.pledges = pledges
        self.parties = parties
        self.where = where
        self.riding = 0

    def set_riding( self, riding ):
        self.where = " politicians.riding_id = " + str( riding.edid )
        self.riding = riding

    def results(self):
        yes_responses = self.get_politician_response_hash('true')
        no_responses = self.get_politician_response_hash('false')

        if self.where == "":
            comment_list = PoliticianPledge.objects.filter(politician__reptype = "M" ).exclude( comments = "")
        else:
            comment_list = PoliticianPledge.objects.filter(politician__reptype = "M" , politician__riding_id = self.riding).exclude( comments = "")

        comment_hash = {}
        for pledge in self.pledges:
            comment_hash[ pledge.id ] = []

        for pledge_w_comment in comment_list:
            comment_hash[pledge_w_comment.pledge_id].append(pledge_w_comment)

        results = []

        for pledge in self.pledges:
            result = PoliticianPledgeTotal( pledge.id, pledge )
            if comment_hash.has_key( pledge.id ):
                result.comments = comment_hash[ pledge.id ]

            for party in self.parties:
                if yes_responses[pledge.id].has_key(party):
                    result.yes_responses.append( yes_responses[ pledge.id ][party] )
                else:
                    result.yes_responses.append("-")
                if no_responses[pledge.id].has_key(party):
                    result.no_responses.append( no_responses[pledge.id][party] )
                else:
                    result.no_responses.append("-")

            results.append(result)
        return( results )

    def get_politician_response_hash(self,supports):
        hash={}
        for pledge in self.pledges:
            hash[ pledge.id ] = {}

        query = "select politicians_pledges.pledge_id, politicians.party, count(politicians.id) from politicians_pledges join politicians on politicians.id = politicians_pledges.politician_id where politicians.reptype='M' and politicians_pledges.supports=" + supports

        if( self.where != "" ):
            query += " and " + self.where

        query += " group by politicians_pledges.pledge_id, politicians.party order by politicians_pledges.pledge_id asc"
        cursor = connection.cursor()
        cursor.execute(query)
        i = cursor.fetchone()

        while i:
            pledge_id, party, total = i[0],i[1],i[2]
            hash[ int(pledge_id) ][party] = total
            i=cursor.fetchone()

        return( hash )

# Standard class for sending an email with this app.  Includes exception handling.

class IBelieveEmail(object):

    def __init__(self, email_name ):
        self.email_name = email_name

    def send(self, to_email, data_hash = {}):
        try:
            subject = render_to_string("emails/" + self.email_name + "/subject.txt", data_hash)
            message = render_to_string("emails/" + self.email_name + "/message.txt", data_hash)
            email = EmailMessage(subject, message, settings.EMAIL_FROM_USER, [to_email])
            email.send()
            return True
        except Exception, e:
            print '%'*78
            print e
            return False

class ConfirmationEmailTemplate(object):

    def __init__( self, confirmation_key, resend = False ):
        self.resend = resend
        self.confirmation_key = confirmation_key

    def send( self, email_addr ):
        activate_url = u'http://%s/join/confirm/%s/' % (unicode(settings.SITE_ROOT), self.confirmation_key)
        if self.resend :
            email = IBelieveEmail("resend_confirm")
        else:
            email = IBelieveEmail("confirmation")
        return(email.send( email_addr, {"activate_url": activate_url,}) )
