import json
import torch
from transformers import AutoModelForSequenceClassification
import transformers
import os
import re
from unidecode import unidecode
from rapidfuzz import fuzz
from huggingface_hub import login

#your Hugging Face Key
login("your-key")

#list of toxic expressions in French
lexique_toxique = {"7allouf", "abruti",
"aller chier", "aller niquer sa mère", "aller se faire enculer", "aller se faire endauffer", "aller se faire foutre", "aller se faire mettre",
"aller se faire pendre", "allez vous faire foutre", "andouille", "archicon", "bande d’abrutis", "beauf", "bête", "bête comme ses pieds",
"bête comme un âne", "biatch", "bite", "bolosse", "bouffon", "bouffonne", "bougnoul", "bougnoule", "branleur", "branleuse",
"casse-couille", "casse-couilles", "cassos", "charogne", "chbeb", "chiabrena", "chienne", "chinetoc", "chinetoque", "Chinetoque",
"chintok", "chnoque", "con", "con comme la lune", "conasse", "connard", "connarde", "connasse", "conne", "couille molle",
"crétin", "débile", "du schnoc", "ducon", "emmerdeur", "emmerdeuse", "enculé", "enculé de ta race", "enculer", "enfant de pute",
"enfant de salaud", "enflure", "enfoiré", "enfoirée", "envoyer faire foutre", "épais", "espèce de", "espingoin", "espingouin",
"être pédé comme un phoque", "face de chien", "FDP", "féminazie", "fermer sa gueule", "fille de pute", "fils de bâtard", "fils de chien",
"fils de chienne", "fils de pute", "fils de ta race", "fiotte", "fumier", "gland", "glandeur", "glandeuse", "glandouillou",
"gogol", "gogol88", "gogole", "gogolito", "grognasse", "gros lard", "imbécile", "incapable", "lâche", "merde", "merdeuse",
"merdeux", "michto", "minable", "minus", "misérable", "moins-que-rien", "mongol", "moricaud", "naze", "nazi", "nègre", "négro",
"nique sa mère", "nique ta mère", "niquer", "niquer sa mère", "niquer sa reum", "niquez votre mère", "noob", "ntm", "NTM",
"ntr", "ordure", "pak pak", "pak-pak", "pakos", "pakpak", "pédale", "pédé", "pétasse", "petite bite", "petite merde", "pignouf",
"pignoufe", "pleutre", "plouc", "poundé", "poundée", "putain de ta race", "pute", "putois", "sac à merde", "salaud", "salaude",
"salop", "salope", "sans-couilles", "sous-merde", "ta bouche", "ta gueule", "ta mère", "ta mère la pute", "ta race", "tafiole",
"tafiotte", "tapette", "tarlouze", "tebé", "tête de con", "tête de gland", "teubé", "tocard", "trou de cul", "trou du cul", 
"trouduc", "va te faire foutre", "zizi", "noob", "retard", "dog", "ape", "trash", "monkey", "autistic", "get c", "get cancer",
"kys", "inter", "random", "hardstuck", "end it", "slit it", "go ff", "ff 15", "go next", "open mid",
"yes, next", "cringe dog", "egirl", "e-whore", "boosted", "bot", "spam ping", "troll", "nigger", "go die",
"0/1 irl", "pisslow", "pedophile", "worm", "chinese monkey", "hang yourself", "slit your throat", "handless",
"disabled", "slut", "dogshit", "muslim terrorist", "muslim rapist", "incel", "faggot", "mom go sky", "mom boom", "death chamber asap",
"dirty rat", "rapist", "nazi", "french surrender", "slit your wrist", "scumbag", "wheelchair gaming", "down syndrom", "midget",
"molested", "jew", "couilles", "debilos", "fdp", "fils de pute", "baise ta mère", "baise tes morts", "bz ta mère", "bz tes morts", "suce", "suceur",
"aller niquer sa mère", "aller se faire enculer", "aller se faire foutre","aller se faire mettre","allez vous faire foutre","avoir de la merde dans les yeux",
"baise", "baiseur", "bangala", "beuteu","biatch","bitch","bite", "bougnoul","bougnoule","bougnouliser", "branlée","couille", "enculé", "enfoiré", "ferme ta geule", "fils de chien",
"fils de chienne", "teubé", "trouduc"
}

# Text normalization function
def normalize(text: str) -> str:
    txt = re.sub(r'@\S+', ' ', text)
    txt = txt.lower()
    txt = unidecode(txt)                       # é → e
    txt = re.sub(r'[^a-z0-9\s]', ' ', txt)     # deletes punctuation
    txt = re.sub(r'(.)\1{2,}', r'\1\1', txt)   # reduces repetitions of more than 2 letters
    # map leet-speak
    leet = str.maketrans({'3':'e','4':'a','1':'i','0':'o','5':'s','7':'t'})
    txt = txt.translate(leet)
    return txt

# Classify a text as if it is toxic or not by using the list of toxic expressions
def is_toxic_lexicon(msg: str, lexique: set, threshold: int = 90) -> bool:
    norm = normalize(msg)
    tokens = norm.split()                # cut into words
    fusion = norm.replace(" ", "")       # remove spaces (we want to test with spaces and without spaces)

    for term in lexique:
        # ignore the very short ones at all (<=2 letters)
        if len(term) <= 2:
            continue

        # for 3 letters, we only match on exact token
        if len(term) == 3:
            if term in tokens :
                return True
            else:
                continue

        # for 4 letters, we match on exact token and fusion
        if len(term) == 4:
            if term in tokens or term in fusion :
                return True
            else:
                continue

        # for long terms (5+), we first perform an exact substring on the merge
        if len(term) >= 5 and term in fusion:
            return True

        # fuzzy-partial for the same long terms
        if len(term) >= 5 and fuzz.ratio(term, fusion) >= threshold:
            return True
    return False

# removes any word beginning with the prefix
def strip_emotes(norm_msg : str, prefix : str) -> str :
    return re.sub(r'\b' + prefix + r'\w*\b', '', norm_msg)


if __name__ == "__main__":

    #configuration of our model
    model = AutoModelForSequenceClassification.from_pretrained('textdetox/twitter-xlmr-toxicity-classifier')
    tokenizer = transformers.AutoTokenizer.from_pretrained('textdetox/twitter-xlmr-toxicity-classifier')
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)

    #input and output directory
    INPUT_DIR_1  = "directory/where/you/saved/chat/of/a/streamer"
    OUTPUT_DIR_1 = "output/directory" 

    #emote prefix
    emote_prefix = ''

    for filename in os.listdir(INPUT_DIR_1) :

        input_path  = os.path.join(INPUT_DIR_1, filename)
        base, _     = os.path.splitext(filename)
        output_name = f"{base}_classified.json"
        output_path = os.path.join(OUTPUT_DIR_1, output_name)

        with open(input_path,"r", encoding="utf-8") as f:
            data = json.load(f)

        #classification
        step = 0
        for entry in data:

            #normalize and clean the message
            raw_msg = entry["message"]
            norm_msg = strip_emotes(raw_msg, emote_prefix)
            norm_msg = normalize(norm_msg)
    

            #try with the lexicon
            if is_toxic_lexicon(norm_msg, lexique_toxique):
                entry["classification"] = "Toxic"
                entry["method"]         = "Lexicon"

            #NLP model
            else:
                batch = tokenizer.encode(norm_msg, return_tensors="pt", truncation = True).to(device)
                with torch.no_grad():
                    output = model(batch)
                    logits = output.logits
                    predicted_class = torch.argmax(logits, dim=1).item()
                entry["classification"] = "Not Toxic" if predicted_class == 0 else "Toxic"
                entry["method"]         = "NLP"
            
            step +=1
            print(step/len(data)*100, "%")

        filtered = []
        for entry in data:
            filtered.append({
                "message"       : entry.get("message", ""),
                "date"          : entry.get("date",    ""),
                "classification": entry.get("classification", ""),
                "method"        : entry.get("method", "")
            })

        # save the classification in a json
        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(filtered, out_f, ensure_ascii=False, indent=2)
