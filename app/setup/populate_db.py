# encoding: utf-8

#
# Script to populate the database with test data.
#
# adds:
#     randomly generated voters from two ridings
#     randomly generated politicians
#     randomly generated pledges and comments


import sys
import os
import time
from django.contrib.webdesign.lorem_ipsum import  *
import random


path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
sys.path.append(path)
from app.mainapp.models import PARTIES, Politician, Riding, Signup, Pledge, PoliticianPledge, EmailConfirmation

# replace with a list of emails you have access to.
EMAILS = ["jenniferlianne@yahoo.ca", "jennifer@visiblegovernment.ca" ]


def get_pledge_hash( pledges, probability_of_yes, comment = False ):
    """
    Generate a hash of pledge values as if it were generated by a form
    pledges: pledges from database
    probability_of_yes: array - probability for each pledge that there's a yes answer
    comments: boolean -- include a comment
    """
    pledge_hash = {}
    for i in range(0, len(pledges)):
        val = random.random()
        if val < probability_of_yes[i]:
            pledge_hash[ pledges[i].code] = ""
        if comment:
            pledge_hash[ "comment-" + pledges[i].code ] = paragraphs( 1 )[0]
    return( pledge_hash )

def create_politicians(ridings):

    # add a politician from each riding
    for riding in ridings:
        party = random.choice(PARTIES.keys())
        pid = str(riding.edid) + PARTIES[party]
        politician = Politician( id = pid,
                                 fname = random.choice( WORDS ).title(),
                                 lname = random.choice( WORDS ).title(),
                                 email = random.choice( EMAILS ),
                                 riding_id = riding,
                                 province = riding.province,
                                 party = party,
                                 reptype = "M" )
        politician.save()

def create_politician_pledges( pledges ):
    # add 50 politician pledges, 5 of whom made comments
    politicians = Politician.objects.all()[0:50]
    count = 0

    for politician in politicians:
        pledge_hash = get_pledge_hash( pledges, [ 1, .90, .5 , 1 , .5 ], count % 10 == True )
        politician.save_pledges(pledge_hash)
        try:
            politician.save()
        except Exception, e:
            print '%'*78
            print e
            return False

        count = count + 1

def create_voters(pledges,ridings):
    # add 120 voters from 12 different ridings.
    ridings = Riding.objects.filter().order_by('?')[0:12]
    for i in range(1,120):
        riding = ridings[ random.randrange(0,11) ]
        voter = Signup( name = (random.choice(WORDS) + " " + random.choice(WORDS)).title()  ,
                        email = random.choice(EMAILS),
                        riding = riding,
                        province = riding.province,
                        verified = True )
        voter.save()
        pledge_hash = get_pledge_hash( pledges, [ 1, .90, .8 , 1 , .7 ])
        voter.save_pledges( pledge_hash )
        EmailConfirmation.objects.create_confirmation_key(voter)

def main():

    random.seed()
    pledges = Pledge.objects.all()
    ridings = Riding.objects.all()


    if Politician.objects.count() < 50:
        create_politicians(ridings)

    if PoliticianPledge.objects.count() == 0:
        create_politician_pledges( pledges )

    if Signup.objects.count() < 10 :
        create_voters( pledges, ridings )



if __name__ == '__main__':
    main()
