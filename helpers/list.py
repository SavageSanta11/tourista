from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer

model = SentenceTransformer('all-MiniLM-L6-v2')

next_words = ['next','tell next','bring to following','after','want to move on',
    'want the next place',
    'provide the next place',
    'next place',
    'next location',
    'next attraction',
    'next stop',
    'next destination',
    'next site',
    'next landmark',
    'next point of interest',
    'next poi',
    'next place',
    'want to go to the next place',
    'want to proceed',
    'proceed',
    'subsequent',
    'subsequent place',
    'subsequent location',
    'subsequent attraction',
    'subsequent stop',
    'subsequent destination',
    'subsequent site',
    'subsequent landmark',
    'subsequent point of interest',
    'subsequent poi',
    'proceed to the following',
    'go to the following',
    'come after',
    'follow up',
    'follow the previous',
    'pursue the next',
    'move to the subsequent',
    'advance to the next place',
    'progress to the next location',
    'journey to the next attraction',
    'continue to the next stop',
    'travel to the next destination',
    'visit the next site',
    'explore the next landmark',
    'check out the next point of interest',
    'reach the subsequent poi',
    'aspire to the next place',
    'desire to go to the subsequent location',
    'crave the subsequent attraction',
    'hope for the next stop',
    'aim for the subsequent destination',
    'look forward to the next site',
    'anticipate the subsequent landmark',
    'wish to see the next point of interest',
    'aim for the next poi',
    'expect the following',
    'foresee the next',
    'predict the subsequent',
    'foretell the following',
    'imagine the next place',
    'visualize the subsequent location',
    'picture the subsequent attraction',
    'envision the next stop',
    'think about the subsequent destination',
    'contemplate the next site',
    'plan to explore the subsequent landmark',
    'scheme to reach the next point of interest',
    'contemplate the next poi',
    'consider the following',
    'regard the subsequent',
    'view the next place',
    'observe the subsequent location',
    'watch the subsequent attraction',
    'survey the next stop',
    'scrutinize the subsequent destination',
    'inspect the next site',
    'examine the subsequent landmark',
    'analyze the next point of interest',
    'assess the subsequent poi',
    'check the following',
    'verify the subsequent',
    'validate the next place',
    'confirm the subsequent location',
    'ascertain the subsequent attraction',
    'ensure the next stop',
    'double-check the subsequent destination',
    'authenticate the next site',
    'substantiate the subsequent landmark',
    'justify the next point of interest',
    'corroborate the subsequent poi',
    'make certain of the following',
    'ensure the subsequent',
    'secure the next place',
    'guarantee the subsequent location',
    'warrant the subsequent attraction',
    'assure the next stop',
    'promise the subsequent destination',
    'pledge the next site',
    'commit to the subsequent landmark',
    'vouch for the next point of interest',
    'swear by the subsequent poi',
    'hand over to the following',
    'transfer to the subsequent',
    'pass to the next place',
    'relay to the subsequent location',
    'convey to the subsequent attraction',
    'give the next stop',
    'present the subsequent destination',
    'bestow the next site',
    'entrust the subsequent landmark',
    'delegate the next point of interest',
    'assign the subsequent poi',
    'offer the following',
    'provide the subsequent',
    'supply the next place',
    'furnish the subsequent location',
    'equip the subsequent attraction',
    'deliver the next stop',
    'yield the subsequent destination',
    'cater the next site',
    'accommodate the subsequent landmark',
    'cater the next point of interest',
    'serve the subsequent poi',
    'done here',
    'done with place',
    'done with location',
    'done with attraction',
    'done with stop',
    'done with destination',
    'done with site',
    'done with landmark',
    'done with point of interest',
    'done with poi',
    'done with place',
    'finished here',
    'finished with place',
    'finished with location',
    'finished with attraction',
    'ready for the next',
    'ready for the next location'
    'ready for the next place',
    'ready for the next place to visit',
    'ready for the next place to go',
    'ready to go',
    'ready to move on',
    'ready to proceed' ]

here_words = [
    'i\'m here',
    'here',
    'have arrived',
    'I arrived',
    'arrived',
    'got there',
    'reached',
    'have reached',
    'am at',
    'I am at the location',
    'I got to the location',
    'I have got to the location',
    'got to the place',
    'have got to the place',
    'have arrived at the place',
    'have arrived at the location',
    'have arrived at the destination',
    'have arrived at the site',
    'have arrived at the landmark',
    'have arrived at the point of interest',
    'have arrived at the poi',
    'here at',
    'arrived at',
    'close by',
    'nearby',
    'near',
    'close',
    'almost there',
    'near to this spot',
    'approached',
    'having reached this point',
    'present at this location',
    'attained this place',
    'achieved this destination',
    'arrived here',
    'reached this spot',
    'made it to the site',
    'attained the landmark',
    'arrived at the point of interest',
    'arrived nearby',
    'in proximity to this place',
    'near to the destination',
    'in the vicinity of',
    'close to this point',
    'nearly there',
    'in the immediate vicinity',
    'at this precise location',
    'standing at this place',
    'encountered this site',
    'reached the landmark',
    'reached the point of interest',
    'right here',
    'hit the place',
    'found oneself at the location',
    'come to this destination',
    'come upon this site',
    'discovered the landmark',
    'stumbled upon the point of interest',
    'achieved the poi',
    'made it here',
    'attained this location',
    'arrived at this destination',
    'reached this site',
    'reached this landmark',
    'made it to the poi',
    'reached here',
    'arrived here',
    'have come',
    'have reached this place',
    'have arrived at this location',
    'have attained this destination',
    'have come upon this site',
    'have discovered the landmark',
    'have stumbled upon the point of interest',
    'have achieved the poi',
    'have made it here',
    'have arrived here',
    'have arrived at this place',
    'have arrived at this location',
    'have arrived at this destination',
    'have arrived at this site',
    'have arrived at this landmark',
    'have arrived at this point of interest',
    'have arrived at this poi',
    'have come here',
    'have reached here',
    'have come to this place',
    'have reached this location',
    'have come to this destination',
    'have come to this site',
    'have come to this landmark',
    'have come to this point of interest',
    'have come to this poi',
    'have arrived over here',
    'have come over here',
    'have reached this spot',
    'have arrived nearby',
    'have reached the place',
    'have arrived in the vicinity of',
    'have come close to this point',
    'have nearly reached the destination',
    'have reached almost there',
    'have come to the immediate vicinity',
    'have arrived at this precise location',
    'have stood at this place',
    'have encountered this site',
    'have reached the landmark',
    'have arrived at the point of interest',
    'have arrived right here',
    'have hit the place',
    'have found oneself at the location',
    'have come to this destination',
    'have come upon this site',
    'have discovered the landmark',
    'have stumbled upon the point of interest',
    'have achieved the poi',
    'have made it here',
    'have attained this location',
    'have arrived at this destination',
    'have reached this site',
    'have reached this landmark',
    'have made it to the poi',
    'have arrived here',
    'have arrived over here',
    'have come over here',
    'have reached this spot',
    'have arrived nearby',
    'have reached the place',
    'have arrived in the vicinity of',
    'have come close to this point',
    'have nearly reached the destination',
    'have reached almost there',
    'have come to the immediate vicinity',
    'have arrived at this precise location',
    'have stood at this place',
    'have encountered this site',
    'have reached the landmark',
    'have arrived at the point of interest',
    'have arrived right here',
    'have hit the place',
    'have found oneself at the location',
    'have come to this destination',
    'have come upon this site',
    'have discovered the landmark',
    'have stumbled upon the point of interest',
    'have achieved the poi',
    'have made it here',
    'have attained this location',
    'have arrived at this destination',
    'have reached this site',
    'have reached this landmark',
    'have made it to the poi',
    'have arrived here',
]

exit_words =  [
    "halt",
    "cease",
    "terminate",
    "finish",
    "end",
    "conclude",
    "terminate",
    "abort",
    "discontinue",
    "quit",
    "leave",
    "depart",
    "withdraw",
    "retreat",
    "evacuate",
    "vacate",
    "abandon",
    "desist",
    "halt",
    "pause",
    "break",
    "finish",
    "complete",
    "wrap up",
    "halt",
    "cease",
    "stoppage",
    "exit",
    "go out",
    "get out",
]

hello_words = ['Hi', 'Hey', 'Greetings', 'Salutations', 'Howdy', 'Good day', 'What\'s up', 'Wassup', 'Yo', 'Sup', 'How\'s it going', 'Hiya', 'How are you', 'Welcome',
              'Hi there', 'G\'day', 'Hello there', 'How are things', 'Good morning', 'Good afternoon', 'Good evening', 'Good night', 'Good day', 'Good to see you', 
              'Hello my friend', 'Hello man', 'hello bro', 'greetings my friend', 'hello my freind', 'what\'s up my friend', 'Hello', 'Hello freind', 'hey friend', 'hey bro',
              'hi friend', 'hi bro', 'hi buddy', 'hey buddy', 'hello buddy', 'hiya buddy', 'hey there', 'hi there', 'hello there', 'hiya there', 'hey mate', 'hi mate', 'hello mate']

pref_phrases = [
    "make my tour about",
    "my preference is",
    "i'm interested in",
    "organize my trip focused on",
    "construct the trip so it features",
    "make the attractions centered around",
    "i want my trip to be about",
    "include attractions concerning",
    "develop a travel plan that revolves around",
    "i want my trip to teach be about",
    "i love learning about",
    "include in my itenerary",
    "build a trip that emphasizes",
    "arrange my sightseeing based on",
    "design a tour that highlights",
    "i have a keen interest in",
    "i'm intrigued by",
    "we're fascinated by",
    "i'm curious about",
    "i'm drawn to",
    "i have a passion for",
    "i am enthusiastic about",
    "i was excited about",
    "i am inclined towards",
    "my interests include",
]

skip_place = ["placeholder"]

skip_words = [
    "skip",
    "skip this place",
    "skip location",
    "pass",
    "ignore",
    "avoid",
    "i don't want to go to",
    "not interested in",
    "not interested in this place",
    "proceed without",
    "go without",
    "exclude",
    "bypass",
    "overlook",
    "disregard",
    "leave out",
    "dismiss",
    "omit",
    "forfeit",
    "neglect",
    "abstain from",
    "refrain from",
    "opt out of",
    "shy away from",
    "give a miss to",
    "i don't like",
    "i dislike",
    "i hate",
    "remove from itinerary",
    "remove from tour"
]

here_enc = list(map(model.encode, here_words))
next_enc = list(map(model.encode, next_words))
tour_enc = list(map(model.encode, ['tour', 'attractions', 'trip']))
exit_enc = list(map(model.encode, exit_words))
hello_enc = list(map(model.encode, hello_words))
skip_enc = list(map(model.encode, skip_words))
skip_place_enc = list(map(model.encode, skip_place))

def update_skip(tour):
    global skip_place
    global skip_place_enc
    skip_place = tour
    skip_place_enc = list(map(model.encode, skip_place))
    print(skip_place)

def similarity_score(cat, user_in):
    in_encode = model.encode(user_in)
    encodes  = None

    if cat == 'here': 
        encodes = here_enc
    elif cat == 'next': 
        encodes = next_enc 
    elif cat == 'exit':
        encodes = exit_enc
    elif cat == 'hello':
        encodes = hello_enc
    elif cat == 'tour':
        encodes = tour_enc
    elif cat == 'skip_intent':
        encodes = skip_enc
    else:
        encodes = skip_place_enc
         
    most_sim = -1
    for word_enc in encodes:
        most_sim = max(util.pytorch_cos_sim(in_encode, word_enc).item(), most_sim)
    return most_sim

def find_highest_sim(cat, user_in):
    in_encode = model.encode(user_in)
    encodes  = None

    if cat == 'here': 
        encodes = here_enc
    elif cat == 'next': 
        encodes = next_enc 
    elif cat == 'exit':
        encodes = exit_enc
    elif cat == 'hello':
        encodes = hello_enc
    elif cat == 'tour':
        encodes = tour_enc
    elif cat == 'skip_intent':
        encodes = skip_enc
    else:
        encodes = skip_place_enc
         
    sim_list = []
    largest_index = 0
    for word_enc in encodes:
        # gives list of similarity scores
        sim_list.append(util.pytorch_cos_sim(in_encode, word_enc).item())
    # find the highest num in this list, return the index, then find the word it is attached to
    for i in range(1, len(sim_list)):
        if sim_list[i] > sim_list[largest_index]:
            largest_index = i
    # returns index num of the place with highest sim
    return largest_index

def preference_parsing(msg):
    pref_phrases.append(msg)
    vectorizer = TfidfVectorizer(use_idf=True)
    X = vectorizer.fit_transform(pref_phrases)
    preference = vectorizer.inverse_transform(X)[len(pref_phrases) - 1][0]
    return preference