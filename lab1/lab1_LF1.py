# python 3.7
import boto3

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_intent(session_attributes, fulfillment_state,message):
    return {
        #'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitIntent',
            #'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def greeting(intent_request):
    return elicit_intent(intent_request['sessionAttributes'], 
                         'Fulfilled',
                         {'contentType': 'PlainText',
                          'content': 'Hi there, how can I help?'})

def validate_dining_suggestions(location, cuisine, dining_time, people_number, phone_number):
    cuisine_types = ['seafood', 'chinese', 'japanese', 'burgers', 'italian', 'thai', 'steakhouses']
    if cuisine is not None and cuisine.lower() not in cuisine_types:
        return build_validation_result(False,
                                       'Cuisine',
                                       'Sorry, we only provide Seafood, Chinese, Japanese, Burgers, Italian, Thai, Steakhouses.')
    if phone_number is not None and (len(phone_number)!=12 or phone_number[:2]!='+1' or not phone_number[2:].isnumeric()):
        return build_validation_result(False,
                                       'PhoneNumber',
                                       'Sorry, we only accept US number. And you phone number should start with +1 followed by 9 digits.')
    return build_validation_result(True, None, None)

def dining_suggestions(intent_request):
    location = get_slots(intent_request)['Location']
    cuisine = get_slots(intent_request)['Cuisine']
    dining_time = get_slots(intent_request)['DiningTime']
    people_number = get_slots(intent_request)['NumberOfPeople']
    phone_number = get_slots(intent_request)['PhoneNumber']
    
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_dining_suggestions(location, cuisine, dining_time, people_number, phone_number)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

        return delegate(output_session_attributes, get_slots(intent_request))

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='Q1')
    response = queue.send_message(
        MessageBody='Dining Information', 
        MessageAttributes={
            'location':{'StringValue':location, 'DataType':'String'},
            'cuisine':{'StringValue':cuisine, 'DataType':'String'},
            'dining_time':{'StringValue':dining_time, 'DataType':'String'},
            'people_number':{'StringValue':people_number, 'DataType':'String'},
            'phone_number':{'StringValue':phone_number, 'DataType':'String'}
        }
    )

    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks. You are looking for {} restaurants at {}, {} holding {} people. Your phone number is {}. Suggestions will be sent to you by SMS soon. Expect my suggestions shortly! Have a good day.'.format(cuisine, location, dining_time, people_number, phone_number)})

def thankyou(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You are welcome.'})


def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'GreetingIntent':
        return greeting(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return dining_suggestions(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thankyou(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    return dispatch(event)
