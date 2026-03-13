import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 1. Training Data Creation (Hardcoded examples)
# Ensure at least 20 examples per tier.
# 1. Training Data Creation (Hardcoded examples)
# Ensure at least 20 examples per tier. 200+ total examples to ensure accuracy.
# 1. Training Data Creation (Hardcoded examples)
# Ensure at least 20 examples per tier. 200+ total examples to ensure accuracy.
data = [
    # Tier 1: Trolling (General insult, no direct threat/harm)
    ("you are stupid", 1), ("dumbest thing ever", 1), ("who let this idiot online", 1),
    ("your content is trash", 1), ("ugly dog", 1), ("no one cares about you", 1),
    ("ratioed", 1), ("L + ratio + you fell off", 1), ("clown behavior", 1),
    ("delete your account", 1), ("tu chutiya hai kya", 1), ("sabse bakwas video", 1),
    ("pagal aurat", 1), ("brainless idiot", 1), ("kuch bhi mat bol", 1),
    ("this is cringe", 1), ("stop posting you are embarrassing yourself", 1),
    ("0 IQ take", 1), ("you look like a cheap imitation", 1), ("absolute garbage opinion", 1),
    ("you cant even speak properly", 1), ("waste of time", 1), ("nobody likes you", 1),
    ("unfollowed", 1), ("this is so pathetic", 1), ("are you normally this dumb", 1),
    ("kya bakwas kar rahi hai", 1), ("go touch grass", 1), ("attention seeker", 1),
    ("get a life bro", 1), ("you sound like a baby", 1), ("boring content", 1),
    ("why do you even try", 1), ("literally no one asked", 1), ("you are irrelevant", 1),
    ("stop begging for likes", 1), ("so annoying to watch", 1), ("cringe fest", 1),
    ("you have zero talent", 1), ("just uninstall the app", 1), ("kya mazaak chal raha hai", 1),
    ("total waste of internet data", 1), ("you talk too much nonsense", 1), ("fake personality", 1),
    ("stop seeking validation", 1), ("not funny at all", 1), ("you look ridiculous", 1),
    ("nobody wants to see this", 1), ("why are you acting smart", 1), ("typical keyboard warrior", 1),
    ("your voice is annoying", 1), ("you know nothing", 1), ("this makes me lose braincells", 1),
    ("loser behavior", 1), ("so sad to watch", 1), ("you are a joke", 1), ("lame video", 1),

    # Tier 2: Hate Speech (Severe abuse, targeted harassment, caste/religion slurs)
    ("you people are a disease and need to die", 2), ("ugly piece of trash go kill yourself", 2),
    ("shakal dekhi hai apni kutiya", 2), ("chinal randi ki aulaad", 2),
    ("go back to the kitchen where you belong", 2), ("women like you are the reason for all problems", 2),
    ("teri aukat kya hai chamar", 2), ("terrorist sympathizer get out of india", 2),
    ("all you feminists should be shot", 2), ("gas chamber you all", 2), ("dirty whore", 2),
    ("tu rann hai sabko pata hai", 2), ("bitch stop talking or else", 2),
    ("bloody illiterate dog", 2), ("you deserve to be beaten up daily", 2), ("tumhari jaat hi aisi hai", 2),
    ("kaminey log sala desh barbaad kar rahe hain", 2), ("harami aurat tera mooh kaal karo", 2),
    ("someone slap this bitch", 2), ("I hope you suffer every day", 2), ("fucking slut nobody loves you", 2),
    ("randi madarchod", 2), ("saali kutiya", 2), ("die in hell", 2), ("hope you get cancer", 2),
    ("your entire community is trash", 2), ("you low caste scum", 2), ("bhangi kahin ki", 2),
    ("we need to cleanse people like you", 2), ("you anti national pig", 2), ("burn in hell bitch", 2),
    ("kill yourself no one will care", 2), ("you deserves worse", 2), ("bloody prostitute", 2),
    ("chudail kahi ki", 2), ("teri maa baap ne yahi sikhaya", 2), ("gas the lot of you", 2),
    ("filthy animal", 2), ("you should be publicly shamed", 2), ("stone her to death", 2),
    ("yeh sab randi khana band karo", 2), ("aurat ki yahi aukat hai", 2), ("tum log kachra ho", 2),
    ("stop breathing oxygen", 2), ("you are a mistake", 2), ("i spit on people like you", 2),
    ("feminazi bitch", 2), ("you should be wiped out", 2), ("hang yourself", 2),
    ("tum jaisi ko jala dena chahiye", 2), ("deshdrohi kutti", 2), ("I will ruin your reputation", 2),
    ("dirty swine", 2), ("go rot in hell", 2), ("filthy scammer community", 2), ("disgusting creature", 2),

    # Tier 3: Sexual Threat (Blackmail, NCII threats, rape threats)
    ("i will leak your pics", 3), ("you owe me nudes or everybody finds out", 3),
    ("send me 10000 rs or i upload the video", 3), ("i have your private photos", 3),
    ("wait till your family sees what you sent me", 3), ("i will r*pe you", 3),
    ("bala*kar kar dunga tera", 3), ("raat ko akeli mat nikalna utha lunga", 3),
    ("teri nangi photo viral karunga", 3), ("pay me or your morphed photos go on telegram", 3),
    ("mera nanga video kal net pe aayega", 3), ("i will post your numbers on escort groups", 3),
    ("send bob and vagene or leak", 3), ("nude bejh warna sabko bataunga", 3),
    ("I recorded our video call", 3), ("your morphed deepfake is ready pay 50k", 3),
    ("main teri mms leak kar dunga", 3), ("tere saare photos edit karke site pe dalunga", 3),
    ("I know your husband i will send him everything", 3), ("give me what i want or your life is ruined", 3),
    ("you will be my slave now", 3), ("i will strip you naked", 3), ("tujhe bed pe le jaunga", 3),
    ("kapde utaar video call pe", 3), ("if you block me i will leak everything", 3),
    ("send 50,000 to my account or your nudes go public", 3), ("I am going to post your naked pics online", 3),
    ("you are my property now", 3), ("I will send this to your boss", 3), ("teri izzat mitti mein mila dunga", 3),
    ("your parents will see this video tonight", 3), ("pay up or face the consequences", 3),
    ("deepfake is ready, 1 lakh transfer kar", 3), ("i will make you do dirty things", 3),
    ("mera bistar garam kar", 3), ("you cannot hide from me i have your mms", 3),
    ("I will expose your dirty secrets on youtube", 3), ("give me back my money or i leak", 3),
    ("sab aakr tera tamasha dekhenge", 3), ("I will sell your nudes", 3), ("rape karunga tera", 3),
    ("I will force you to sleep with me", 3), ("this video goes to instagram if you say no", 3),
    ("tujhe pure sheher me nanga ghumaunga", 3), ("sab family whatsapp group me photo bhej dunga", 3),
    ("show me your body or else", 3), ("I have hacked your camera", 3), ("you belongs to me now", 3),
    ("I will satisfy myself with you forcibly", 3), ("give into my demands or your reputation is gone", 3),
    ("showing your private parts to everybody", 3), ("your naked album is online", 3), ("time to leak", 3),

    # Tier 4: Credible Danger (Imminent physical harm, location tracking, stalking)
    ("i know where you live", 4), ("im coming for you today", 4),
    ("I am outside your college right now, come out", 4), ("i know you take the metro to Andheri at 6pm", 4),
    ("kal jab tu office jayegi tab dekhta hu", 4), ("i will throw acid on your face", 4),
    ("goli maar dunga saali ko", 4), ("teri botiyan kaat kar phek dunga", 4),
    ("ghar aakar marunga", 4), ("main tere peechay khada hu dekh le", 4),
    ("You have 10 minutes to open the door", 4), ("I brought a knife, see you soon", 4),
    ("mumbai terminal 2 parking mein ruks, main wahi aa raha hu", 4), ("tujhe zinda nahi chhodunga", 4),
    ("i will kidnap your kid from school", 4), ("i have hired someone to finish you", 4),
    ("check your window", 4), ("if you call police you die tonight", 4),
    ("tere baap ko marunga uski dukhan par", 4), ("I am tracking your phone location, you cant hide", 4),
    ("I am waiting near the red car in your building", 4), ("I have a gun", 4), ("I will slit your throat", 4),
    ("kal jab metro me chadhogi", 4), ("i am right behind you", 4), ("look outside your house", 4),
    ("acid daal dunga face par", 4), ("I will murder your entire family", 4), ("tu aaj bachegi nahi", 4),
    ("tujhe ghar se utha lunga", 4), ("i am following you from Dadar station", 4), ("I know where your kids study", 4),
    ("i am outside the mall wait there", 4), ("gla kaat dunga", 4), ("i brought the boys, we are coming up", 4),
    ("i am watching you sleep", 4), ("open the gate or I will break it down", 4),
    ("aaj raat ko tera murder pakka", 4), ("i am carrying a weapon for you", 4),
    ("if you step out of your office you are dead", 4), ("delhi cantt area me mil, maut dunga tujhe", 4),
    ("I have your live location right now", 4), ("i am sitting in the cafe opposite to your house", 4),
    ("hiring shooters to take you down", 4), ("wait till 8pm, you will see what happens", 4),
    ("meri goli se koi nahi bacha sakta", 4), ("I will run my car over you", 4),
    ("I am in the elevator coming to 5th floor", 4), ("tujhe jalakar khaak kar dunga", 4),
    ("waiting outside your house with a gun", 4), ("i know your address and i am here", 4), ("you have 1 hour left", 4)
]

# Duplicate the dataset heavily to give the Tfidf better word clouds per specific intent
data = data * 10


# Convert to DataFrame
df = pd.DataFrame(data, columns=['text', 'label'])

# 2. Pipeline Definition
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
    ('clf', LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced'))
])

X = df['text']
y = df['label']

# 3. Train-Test Split & Evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training model...")
pipeline.fit(X_train, y_train)

print("Evaluating...")
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# 4. Save Model
model_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(model_dir, 'threat_model.pkl')
joblib.dump(pipeline, model_path)
print(f"Model saved to {model_path}")
