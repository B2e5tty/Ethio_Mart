import pandas as pd
from amseg.amharicSegmenter import AmharicSegmenter
import re
import nltk

class Tokenization:
    # intialize the class
    def __init__(self, path):
        self.df = pd.read_csv(path)
        self.tokens = []
    

    # return the dataframe
    def get_dataframe(self):
        return self.df
    
    # describe the dataframe and drop nan value
    def clean(self):
        # info on the dataset
        self.df.info()

        # drop nan message value
        self.df.dropna(subset=['Message'],inplace=True)

        print(f"The shape of the dataframe after dropping NaN values: {self.df.shape}")

    # remove emojis and save the clean data
    def remove_emojis(self):
            def remove(text):
                emoji_pattern = re.compile(
                    "[" 
                    "\U0001F600-\U0001F64F"  # emoticons
                    "\U0001F300-\U0001F5FF"  # symbols & pictographs
                    "\U0001F680-\U0001F6FF"  # transport & map symbols
                    "\U0001F700-\U0001F77F"  # alchemical symbols
                    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                    "\U0001FA00-\U0001FA6F"  # Chess Symbols
                    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                    "\U00002702-\U000027B0"  # Dingbats
                    "\U000024C2-\U0001F251" 
                    "]+", 
                    flags=re.UNICODE
                )
                return emoji_pattern.sub(r'', text)

            # remove emojis
            self.df['emoji_removed'] = self.df['Message'].apply(remove)
            
            # export the message data to csv file
            message_df = self.df.copy()
            self.df.to_csv('clean_message.csv',index=False)
    
    # tokenization functions 
    def new_tokenization(self):
        # Initialize the Amharic segmenter
        sent_punct = []
        word_punct = []
        segmenter = AmharicSegmenter(sent_punct, word_punct)

        tokens = []
        # Example usage with different variable names
        # Tokenize each word/token with associated label
        for line in self.df['emoji_removed']:
            tokenized_word = segmenter.amharic_tokenizer(line)  # Tokenize the word
            tokens.extend(tokenized_word)

        # convert english words to lower case
        tokens = [token.lower() for token in tokens]

        new_tokens = []
        # split tokens contain escape character
        for index, token in enumerate(tokens):
            if '\n' in token:
                tkn = token.replace('\n',' ')
                tkn = tkn.split()
                # print(tkn.split())
                # tkn = ' '.join(tkn.split(" ")).strip()
                new_tokens.extend(tkn)
            else: 
                new_tokens.append(token)

        tokens = new_tokens
        # check
        for index, token in enumerate(tokens):
            if '\n' in token:
                print(token)

        # print(tokens)
        self.tokens = tokens

    # labeling tokens:
    def new_label_tokens(self):
        # products sold in the channels
        product = [
            "romper",
            "baby",
            "bag",
            "mat",
            "breast",
            "milk",
            "collector",
            "box",
            "dipping",
            "jar",
            "baby",
            "bassinet",
            "car",
            "seat",
            "stroller",
            "cradle",
            "basket",
            "safety",
            "belt",
            "bottle",
            "sterilizer",
            "drying",
            "playpen",
            "chair",
            "trimmer",
            "cushioned",
            "storage",
            "warmer",
            "heating",
            "disinfection",
            "underwear",
            "pencil",
            "shirt",
            "cotton",
            "pacifier",
            "shield",
            "case",
            "brush",
            "glove",
            "feeder",
            "organizer",
            "hat",
            "dress",
            "shoe",
            'ማጠቢያ',
            "እቃ",
            "ማጠራቀሚያ",
            "መያዚያ",
            "carier"
        ]

        # dictionary to contain specific token with their labels
        token_label = {}

        for token in self.tokens:
            # match phone numbers
            if re.match(r'^\d{10,}$', token): # numbers
                token_label[token] = 'O'

                # words that ብር or birr   
            elif 'ብር' == token or 'birr' == token:
                token_label[token] = 'B-PRICE'

            # words containing ብር or birr  
            elif 'ብር' in token or 'birr' in token:
                # ብር is in ገብርኤል and (free,size,ሳያልቅቦት,ከመቃብር) are output if considered only the above condition
                if token != 'ገብርኤል' and 'free' not in token and 'size' not in token and 'ሳያልቅቦት' not in token and 'ከመቃብር' not in token:
                    token_label[token] = 'I-PRICE'

                # assign ገብርኤል as location
                elif token == 'ገብርኤል':
                    token_label[token] = 'I-LOC'

                # other as O   
                else:
                    token_label[token] = 'O'

            # locations in the message
            elif 'ገርጂ' in token or 'ብስራተ' in  token or '4ኪሎ' in token or 'ኢምፔሪያል' in token or 'ላፍቶ' in token:
                token_label[token] = 'I-LOC' 

            # products in the message
            elif token in product:
                    if token not in ['baby','milk','breast']:           # succeeding words after ['baby','milk','breast'] are products therefore I considered them as B-Product
                        token_label[token] = 'I-PRODUCT' 

                    else:
                        token_label[token] = 'B-PRODUCT'  
            else: 
                token_label[token] = 'O' 

        # then creating a label list for aligning
        labelled_tokens = []
        for token in self.tokens:
            # print(token)
            labelled_tokens.append([token, token_label[token]])

        return self.tokens, labelled_tokens

    # Convert english to amharic
    def remove_english_word(self, df):
        # dictionary of the words to be changed
        word_dict = {
            "romper": "ሙሉ ልብስ",
            "birr": "ብር",
            "bag": "ቦርሳ",
            "mat": "ምንጣፍ",
            "breast": "ጡት",
            "milk": "ወተት",
            "collector": "ማከማቻ",
            "box": "ሳጥን",
            "dipping": "መንከሪያ",
            "jar": "ማሰሮ",
            "baby": "ህጻን",
            "bassinet": "ህጻን ማስተኛ",
            "car": "መኪና",
            "seat": "መቀመጫ",
            "stroller": "ጋሪ",
            "cradle": "ህጻን ማስተኛ",
            "basket": "ቅርጫ",
            "safety": "ደህንነት",
            "belt": "ቀበቶ",
            "bottle": "ጠርሙስ",
            "sterilizer": "ጀርም ማጥፊያ",
            "drying": "ማድረቂያ",
            "playpen": "መጫወቻ እስክብሪቶ",
            "chair": "መቀመጫ",
            "trimmer": "ጥፍር መቁረጫ",
            "cushioned": "ፍራሽ",
            "storage": "ማከማቻ",
            "warmer": "ማሞቂያ",
            "heating": "ማፍያ",
            "disinfection": "ኢንፌክሽን ማጥፍያ",
            "underwear": "ፑታንታ",
            "pencil": "እርሳስ",
            "shirt": "ቲሸርት",
            "cotton": "ጥጥ",
            "pacifier": "የእንጀራ እናት",
            "shield": "መሸፈኛ",
            "case": "ሻንጣ",
            "brush": "ማበጠሪያ",
            "glove": "የእጅ ልብስ",
            "feeder": "ማብያ",
            "organizer": "መደርደሪያ",
            "hat": "ኮፍያ",
            "dress": "ቀሚስ",
            "shoe": "ጫማ",
            "kids": "ህጻናት",
            "carier": "ማዘያ"  
        }

        words = set(word.lower() for word in nltk.corpus.words.words())

        for index, row in df.iterrows():
            word = row['word'].lower()

            if word in words and word in word_dict.keys():
                df.at[index, 'word'] = word_dict[word]

            elif word in words and word not in word_dict.keys(): 
                df.drop(index, inplace=True)

            else: pass

        # # reset the index
        df.reset_index(drop=True,inplace=True)

        return df
    
    # conll format
    def conll_format(self,df):
        # Save to CoNLL format (with space as separator)
        with open('tokens_labels.conll', 'w',encoding='utf-8') as f:
            for _, row in df.iterrows():
                if row['word'] == '\n':  # Separate sentences
                    f.write('\n')
                else:
                    f.write(f"{row['word']} {row['label']}\n")
            f.write('\n')  # Final blank line at the end
    
        

 