"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib.request
import re
from html_table_parser import parser_functions as parse
from bs4 import BeautifulSoup as bs
import random
# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>"+output+"</speak>"
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the triangle mtb trail status checker.  " \
                    "Tell me what trail you'd like to know about.  " \
                    "You can say, 'is beaver dam open?' or 'list the open trails'.  "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask for a trail status."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

happy_expressions=["Excellent!","Groovy!","Awesome!","Good news!","Cool!","Brilliant!"]
sad_expressions=["Bummer!","Too bad!","Sorry.","Alas!","Oh no!"]

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using triangle mtb trail status."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def massage_trail_name(name):
    name=re.sub("carolina north forest","cnf",name,flags=re.I)
    name=re.sub("carolina north","cnf",name,flags=re.I)
    name=re.sub("harris lake","harris",name,flags=re.I)
    name=re.sub("^brumley$","brumley forest",name,flags=re.I)
    return name

def get_trail_data():
    s = urllib.request.urlopen("http://trianglemtb.com/trailstatus.php").read()
    table=parse.make2d(bs(s,"html.parser")) 
    return table

def filter_trails(data,state):
    trails={}
    for trail in data:
        if re.match(trail[1],state,re.IGNORECASE):
            trails[trail[0]]=trail
    return trails

def get_trail(data,name):
    for trail in data:
        if re.match(trail[0],name,re.IGNORECASE):
            return trail
    return None

def get_open_trails(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    trails=filter_trails(get_trail_data(),"open")
    if len(trails) == 0:
        speech_output="<say-as interpret-as=\"interjection\">%s</say-as>  There are no open trails right now." % random.choice(sad_expressions)
    else: 
        speech_output="The following trails are currently marked as open: "
        comma=""
        for t,trail in trails.items():
            speech_output+=comma
            speech_output+=trail[0]
            comma="<break strength=\"strong\"/>, "
        speech_output+=".  Have a great ride!"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session))

def get_closed_trails(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    trails=filter_trails(get_trail_data(),"closed")
    
    if len(trails) == 0:
        speech_output="<say-as interpret-as=\"interjection\">%s</say-as>  There are no closed trails right now." % random.choice(happy_expressions)
    else:
        speech_output="The following trails are currently marked as closed: "
        comma=""
        for t,trail in trails.items():
            speech_output+=comma
            speech_output+=trail[0]
            comma="<break strength=\"strong\"/>, "
        speech_output+=".  Please don't ride closed trails."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session))

def pick_trail(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    trails=filter_trails(get_trail_data(),"open")
    if len(trails) == 0:
        speech_output="<say-as interpret-as=\"interjection\">%s</say-as>  There are no open trails right now." % random.choice(sad_expressions)
    else: 
        key=random.choice(list(trails.keys()))
        trail=trails[key]
        trail_name=trail[0]
        pieces=trail[3].split(None,1)
        prefix=""
        suffix="You should ride it!"
        speech_output="%s %s is marked as %s as of <say-as interpret-as=\"date\" format=\"md\">%s</say-as> at <say-as interpret-as=\"date\">%s</say-as>. %s" % (prefix, trail_name,trail[1],pieces[0],pieces[1],suffix)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session))

def trail_query(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    trail_name=massage_trail_name(intent['slots']['Trail']['value'])
    trail=get_trail(get_trail_data(),trail_name)
    if trail is None:
        speech_output="Sorry, I couldn't find any information for a trail named %s." % trail_name
    else:
        if re.match(trail[1],"open",re.IGNORECASE):
            prefix="<say-as interpret-as=\"interjection\">%s</say-as>" % random.choice(happy_expressions)
            suffix="Have a great ride!"
        else:
            prefix="<say-as interpret-as=\"interjection\">%s</say-as>" % random.choice(sad_expressions)
            suffix="Please don't ride the closed trails."
        pieces=trail[3].split(None,1)
        speech_output="%s %s is marked as %s as of <say-as interpret-as=\"date\" format=\"md\">%s</say-as> at <say-as interpret-as=\"date\">%s</say-as>. %s" % (prefix, trail_name,trail[1],pieces[0],pieces[1],suffix)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "OpenTrails":
        return get_open_trails(intent, session)
    elif intent_name == "ClosedTrails":
        return get_closed_trails(intent, session)
    elif intent_name == "TrailQuery":
        return trail_query(intent, session)
    elif intent_name == "PickTrail":
        return pick_trail(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
#    if (event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.amzn1.ask.skill.a8a22739-3be4-42bf-9883-6ed794bdb0af"):
#         raise ValueError("Invalid Application ID")
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.a8a22739-3be4-42bf-9883-6ed794bdb0af"):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def main():
    table=get_trail_data()
    #filtered=filter_trails(table,"OPEN")
    #print(filtered)
    #atrail=get_trail(table,"beaver dam")
    #print(atrail)

    trails=filter_trails(get_trail_data(),"open")
    if len(trails) == 0:
        speech_output="Bummer, there are no open trails right now."
    
    print(trails)
    speech_output="The following trails are currently marked as open: "
    comma=""
    for t,trail in trails.items():
        speech_output+=comma
        speech_output+=trail[0]
        comma=","
    speech_output+=".  Have a great ride!"
    print(speech_output)


#main()
