### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    continue_confirmation = get_slots(intent_request)["continueConfirm"]
    us_state = get_slots(intent_request)["stateUS"]
    understood_confirmation = get_slots(intent_request)["understoodConfirm"]
    age = get_slots(intent_request)["age"]
    custodial_acct = get_slots(intent_request)["custodialAccount"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    until_retire = get_slots(intent_request)["untilRetirement"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

    ### YOUR DATA VALIDATION CODE STARTS HERE ###

        slots = get_slots(intent_request)

        validation_result = validate_data(continue_confirmation, us_state, understood_confirmation, 
        age, custodial_acct, investment_amount, until_retire, intent_request, risk_level)

        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None # Cleans invalid slot
            
            # Returns and elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
                )

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    initial_recommendation = get_investment_recommendation(risk_level)

        # Return a message with the initial recommendation based on the risk level.

    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )

def validate_data(continue_confirmation, us_state, understood_confirmation, age, custodial_acct, 
investment_amount, until_retire, intent_request, risk_level):
    # Validate if they would like to continue because they must provide the state they reside in.
    if continue_confirmation is not None:
        continue_confirmation = parse_str(continue_confirmation)
        if continue_confirmation == "Yes":
            return build_validation_result(
                True,
                "continueConfirm",
                "Thank you. Let's continue!")
        elif continue_confirmation == "No":
            return build_validation_result(
                False,
                "continueConfirm",
                "We hope you use our services in the future when you are able to provide this information."
                "We hope you have a good day.")
                
    # Validate what state they live in. Alabama, Deleware, and Nebraska have age requirement of 19 to trade. 
    # Mississippi have age requirement of 21.
    if us_state is not None:
        us_state = parse_str(us_state)
        if state == "AL":
            return build_validation_result(
                True,
                "stateUS",
                "Alabama has an age requirement of 19 to trade without a custodial account.")
        elif state == "DE":
            return build_validation_result(
                True,
                "stateUS",
                "Delaware has an age requirement of 19 to trade without a custodial account.")
        elif state == "NE":
            return build_validation_result(
                True,
                "stateUS",
                "Nebraska has an age requirement of 19 to trade without a custodial account.")
        elif state == "MS":
            return build_validation_result(
                True,
                "stateUS",
                "Mississippi has an age requirement of 21 to trade without a custodial account.")
        else:
            return build_validation_result(
                True,
                "stateUS",
                "Your state has an age requirement of 18 to trade without a custodial account.")
        
    # Validate that they understand the age requirement of the state they reside in.
    if continue_confirmation is not None:
        continue_confirmation = parse_str(continue_confirmation)
        if continue_confirmation == "No":
            return build_validation_result(
                False,
                "continueConfirm",
                "We hope you use our services in the future when you are able to provide this information."
                "We hope you have a good day.")
        
        
    # Validate that age is greater than 19 in Alabama, Delaware, and Nebraska, greater than 21 in Mississippi
    # and 18 in all other states
    if age is not None:
        age = parse_int(age)
        if us_state == "AL" and age <= 19:
            return build_validation_result(
                False,
                "age",
                "You are not of age to trade in Alabama. We hope you return to our services when you are at least 19 years old.")
        elif us_state == "DE" and age <= 19:
            return build_validation_result(
                False,
                "age",
                "You are not of age to trade in Deleware. We hope you return to our services when you are at least 19 years old.")
        elif us_state == "NE" and age <= 19:
            return build_validation_result(
                False,
                "age",
                "You are not of age to trade in Nebraska. We hope you return to our services when you are at least 19 years old.")
        elif us_state == "MS" and age <= 21:
            return build_validation_result(
                False,
                "age",
                "You are not of age to trade in Mississippi. We hope you return to our services when you are at least 19 years old.")
        elif age > 65:
            return build_validation_result(
                False,
                "age",
                "With our services and investment recommendations, our goal is to provide you with an opportunity invest enough money"
                "to retire before the age of 65. Please enter an age that is younger than 65.")
                
   # Validate if they are under the age requirement in their residing state that their parent or guardian has a custodial account.             
    if custodial_acct is not None:
        custodial_acct = parse_str(custodial_acct)
        if state = "AL","NE","DE" and age < 19 and custodial_acct == "Yes":
            return build_validation_result(
                True,
                "custodialAccount",
                "We are glad to hear that. Let's continue!")
        elif state = "AL","NE","DE" and age < 19 and custodial_acct == "No":
            return build_validation_result(
                False,
                "custodialAccount",
                "Unfortunatly, since the age or custodial account requirement is not met, we will not be able to continue your services"
                "at this time. We hope you return to our services when one of the requirements is met.")
        elif state == "MS" and age < 21 and custodial_acct == "Yes":
            return build_validation_result(
                True,
                "custodialAccount",
                "We are glad to hear that. Let's continue!")
        elif state == "MS" and age < 21 and custodial_acct == "No":
            return build_validation_result(
                False,
                "custodialAccount",
                "Unfortunatly, since the age or custodial account requirement is not met, we will not be able to continue your services"
                "at this time. We hope you return to our services when one of the requirements is met.")
        elif age < 18 and custodial == "Yes":
            return build_validation_result(
                True,
                "custodialAccount",
                "We are glad to hear that. Let's continue!")
        else age < 18 and custodial_acct == "No":
            return build_validation_result(
                False,
                "custodialAccount",
                "Unfortunatly, since the age or custodial account requirement is not met, we will not be able to continue your services"
                "at this time. We hope you return to our services when one of the requirements is met.")
                
    # Validate that investment amount is greater than 5000
    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investmentAmount",
                "The minimum amount to invest should be equal to or greater than $5,000.00, "
                "please provide a greater amount to continue with our services.")
    
    if until_retire is not None:
        until_retire = prase(until_retire)
        till_retire = until_retire - age
        if until_retire > 65:
            return build_validation_result(
                False,
                "untilRetirement",
                "With our services and investment recommendations, we hope to provide you with an opportunity to retire before the age of 65."
                "Please choose an age that at most 65.")
        elif until_retire < 1:
            return build_validation_result(
                False,
                "untilRetirement",
                "With the time constrain at hand, we are unable to ensure success in our services and recommendations. We apologize for"
                "the inconvenience.")
        elif till_retire > 1 and < 12:
            return build_validation_result(
                True,
                "untilRetirement",
                "We recommend ________ risk level to ensure success in your investments. If you choose another option, we understand"
                "and will find options to fit it.")
        elif till_retire > 12 and < 24:
            return build_validation_result(
                True,
                "untilRetirement",
                "We recommend ________ risk level to ensure success in your investments. If you choose another option, we understand"
                "and will find options to fit it.")
        elif till_retire > 24 and < 35:
            return build_validation_result(
                True,
                "untilRetirement",
                "We recommend ________ risk level to ensure success in your investments. If you choose another option, we understand"
                "and will find options to fit it.")
        elif till_retire > 35 and < 47:
            return build_validation_result(
                True,
                "untilRetirement",
                "We recommend ________ risk level to ensure success in your investments. If you choose another option, we understand"
                "and will find options to fit it.")

    # True result will return if age and/or are valid
    return build_validation_result(True, None, None)
    

        ### YOUR DATA VALIDATION CODE ENDS HERE ###

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###


    # Get the initial investment recommendation
def get_investment_recommendation(risk_level):
    risk_levels = {
        "Low": # NEED TO CHANGE THIS TO OUR CODE,
        "Medium": # NEED TO CHANGE THIS TO OUR CODE,
        "High": # NEED TO CHANGE THIS TO OUR CODE,
        "Extreme": # NEED TO CHANGE THIS TO OUR CODE
    }
            
    return risk_levels[risk_level]

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
