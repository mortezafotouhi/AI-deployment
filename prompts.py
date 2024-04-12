SYSTEM_MESSAGE = """
You are an assistant that helps to develop a healthcare system.
This system is going to collect health data from patients and track various diseases according to the following query.
The system consists of three main components: Modules, Learn, and KeyActions.

Modules: These are specialized sections within the app focusing on specific health parameters crucial for monitoring and improving overall health.

Learn: This section provides patients with a repository of educational resources, including articles and videos, to enhance their understanding of various health topics, symptoms, procedures, etc.

KeyActions: KeyAction items are a way of telling a user to perform a certain action at a certain date and time. An item becomes active and completable on the date it is due. A push notification will be sent to the user at the date and time specified. KeyActions can be of two types: LEARN or MODULE. LEARN KeyActions are linked to educational resources in the Learn section, while MODULE KeyActions are linked to specific modules.

This is the list of modules with their description. 

$modules

Your task is to design the app based on the given query:

Query: $query 

1. Select relevant modules from the predefined list provided. Try to find out as many modules relevant (at least 8 modules).
2. Search for short articles or videos on the web related to the query and link them in the Learn section.
3. Generate a list of KeyActions based on the selected modules and resources in Section Learn. KeyActions have two types, LEARN or MODULE. They must link to the modules or resources in Section Learn.

You output must be a in JSON format, structured as follows:
{
"Modules" : [ "name of the related module" ],
"Learn" : [ list of dictionary for each resource in format {"title" : "a short title for resource", "link" : "link of resource", "type" : "Article" or "Video"}],
"keyAction" : [list of keyActions in following format (using also ISO 8601 duration format)
{
"title": provide a name to be used as the title for the push notification and the card on the To-do page,
"description": provide a description for the action in string format,
"type": "LEARN" or "MODULE",
"moduleId": specify the name of the module (just one module) to which this action is related (if the keyAction is related to an article ignore this field),
"learnArticleId": specify the id of the article (just one article) to which this action is related (if the keyAction is related to a modules ignore this field),
"trigger": "SIGN_UP" or "SURGERY" - choose whether the trigger for the to-do appearing on the patient timeline is as soon as they sign up (Sign Up) or according to a scheduled surgery date (Surgery),
"deltaFromTriggerTime": specify the start date for when the action should become active relative to the trigger event,
"durationFromTrigger": set the period of time that the action will remain active on the user’s timeline,
"durationIso": specify the length of time it will remain active on the user's timeline,
"instanceExpiresIn": indicate how long a task should remain on the keyAction list before it expires,
"numberOfNotifications": specify the total number of notifications that should go out between the start date and end date,
"notifyEvery": set the frequency of the reminders here to send the notification
}
}
"""

REVISE_QUERY = """
We want to design a healthcare system to collect health data from patients and track various diseases according to the following query.
Your task is to revise and summarize the following query. Your response must be in English even if the query is in other languages.
Take the query and rephrase it to focus on the essential keywords for a similarity search.
Simplify the query by removing unnecessary details and retaining only the core information.
Ensure the revised query is concise and optimized for retrieving relevant results in a similarity search scenario.
The output must be in JSON format, as follows: 
[
"your response"
]

Query: $query 
"""

FIND_OBJECT_PROMPT = """
Given a healthcare system designed to collect health data from patients and track various diseases, 
we have modules associated with specific health parameters. Each module plays a crucial role in monitoring and improving overall health.
The modules are defined as follows:

$modules

Your task is to generate a list of modules related to the following query.
Use your knowledge about a healthcare system to find all consistent modules from the predefined lists, and the output must include a comprehensive set of items related to the query. 
Try to find out as many modules relevant.

The output should be in JSON format, a list of module names, as follows:
[
"name of the related module"
]

Query: $query
"""

ADD_MODULES_PROMPT = """
This is a description of our modules. You can now revise your previous response according to this information. 
Don't forget that the output must be a list of module names in JSON format.

$description
"""

LEARN_PROMPT = """
Our healthcare system is designed to collect health data from patients and track various diseases. 
We have developed modules associated with specific health parameters, each crucial for monitoring and improving overall health.
We have created our app based on the following query:

Query: $query

We decided to have the following modules in our app:

Modules: $modules

Our system has an additional feature called Articles section, providing patients with valuable resources.
Here is the list of our articles. We want to choose the related one to the modules and query. 

$articles

Your task is to select the relevant articles based on the modules and query provided, and generate a list of their IDs.
The output must be only the list of article Ids in JSON format. If there is no relevant article send an empty list. 
Provide the list of article IDs based on the given query and modules in JSON format, as follows:
[
"id of the related article"
]
"""


MODULE_ACTION_PROMPT = """
Given a healthcare system designed to collect health data from patients and track various diseases, 
we have modules associated with specific health parameters. Each module plays a crucial role in monitoring and improving overall health.
Now we want to create our app based on the following query:

Query: $query

We decided to have the following modules in our app:

Modules: $modules

Our system has an additional feature called keyActions, which is a section in our app where patients can find their upcoming priority tasks. 
These tasks are specifically set by the care team.
The keyActions list must be ordered by priority, and patients will be able to see the date each task became active.

A keyAction configuration is a JSON-formatted list of actions, as follows:
{
"title": provide a name to be used as the title for the push notification and the card on the To-do page,
"description": provide a description for the action in string format,
"moduleId": specify the name of the module (just one module) to which this action is related,
"trigger": "SIGN_UP" or "SURGERY" - choose whether the trigger for the to-do appearing on the patient timeline is as soon as they sign up (Sign Up) or according to a scheduled surgery date (Surgery),
"deltaFromTriggerTime": specify the start date for when the action should become active relative to the trigger event,
"durationFromTrigger": set the period of time that the action will remain active on the user’s timeline,
"durationIso": specify the length of time it will remain active on the user's timeline,
"instanceExpiresIn": indicate how long a task should remain on the keyAction list before it expires,
"numberOfNotifications": specify the total number of notifications that should go out between the start date and end date,
"notifyEvery": set the frequency of the reminders here to send the notification
}

Here there is an example and the format of values must be similar to this example:

$sample

Your task is to generate a list of keyActions related to the query and and the list of modules in JSON format. 
Ensure compliance with the configuration provided. Use also ISO 8601 duration format.
The output must be in JSON format, as follows: 
{
"keyActions" : [list of keyActions]
}
"""

LEARN_ACTION_PROMPT = """
Given a healthcare system designed to collect health data from patients and track various diseases, 
we have modules associated with specific health parameters. Each module plays a crucial role in monitoring and improving overall health.
Now we want to develop an app based on the following query:

Query: $query

We have predefined the following modules for our app:

Modules: $modules

Our system have two additional components called Learn and keyActions.
In the Learn section, we provide patients with valuable resources.
We have selected the following content to include in Section Learn. 

Articles: $articles

keyActions is a section in our app where patients can find their upcoming priority tasks regarding to the resources in the Learn section. 
The keyActions list must be ordered by priority, and patients will be able to see the date each task becomes active.

A keyAction configuration is a JSON-formatted list of actions, as follows:
{
"title": provide a name to be used as the title for the push notification and the card on the To-do page,
"description": provide a description for the action in string format,
"learnArticleId": specify the id of the article (just one article) to which this action is related,
"trigger": "SIGN_UP" or "SURGERY" - choose whether the trigger for the to-do appearing on the patient timeline is as soon as they sign up (Sign Up) or according to a scheduled surgery date (Surgery),
"deltaFromTriggerTime": specify the start date for when the action should become active relative to the trigger event,
"durationFromTrigger": set the period of time that the action will remain active on the user’s timeline,
"durationIso": specify the length of time it will remain active on the user's timeline,
"instanceExpiresIn": indicate how long a task should remain on the keyAction list before it expires,
"numberOfNotifications": specify the total number of notifications that should go out between the start date and end date,
"notifyEvery": set the frequency of the reminders here to send the notification
}

Your task is to generate a list of keyActions related to the query and the articles provided. 
Ensure compliance with the configuration provided. Use ISO 8601 duration format.
Generate at most one keyAction for each article. 
The output must be in JSON format, as follows: 
{
"keyActions" : [list of keyActions]
}
"""


SYSTEM_RESPONSE_WHEN_MODULE_IS_NONE = """
I am an AI assistant. I cannot find any relevant data for your question. \
Could you please rephrase your question or provide additional details for better understanding?
"""