import random, time, math
from IPython.core.display import display, HTML, clear_output
import ipywidgets as widgets
from collections import Counter, OrderedDict
from ipywidgets import Layout

instructions = """The point of the game is to guess words.  First, you will set your difficulty level using the drop-down menus above.  
Next, run the cell below and click the 'fetch word' button. The computer will pick a word at random and show you the 
first letter. The timer will start and you can begin guessing words.

After each guess the computer will provide you with feedback.  A red square means the correct letter has been guessed in 
the correct position, while a yellow circle means the correct letter has been guessed but is in the incorrect position. 
The computer will keep track of your wins and losses.  After each round, you can get a new word by pressing 'fetch word'
once again.  The cell output will clear and you'll see the first letter of the new word."""

instructions_flag = True
reset_flag = True
submit_flag = False
wins, losses = 0, 0
fin = open('words.txt')
words = [line.rstrip('\n') for line in fin]

# Word-picking

def curate_words(words):
    '''applies dropdown value for word length to the list comprehension'''
    return [word for word in words if len(word) == length.value]

def pick_word(words):
    '''picks random word from list'''
    lim = len(words) - 1
    index = random.randint(0,lim)
    return words[index]

# Handling user input

def on_button_clicked(b):
    '''callback function used to show instructions. Global variable chosen as CB functions do not accept parameters'''
    global instructions_flag
    if instructions_flag:
        print(instructions)
        instructions_flag = False
    else:
        clear_output()
        instructions_flag = True
        
def check_time():
    '''checks the amount of time spent on a guess'''
    global losses, timer, reset_flag, submit_flag
    if time.time() - timer > clock.value and submit_flag:
        print("You're out of time! The correct word was: {}\nClick the fetch button to get your next word".format(word))
        losses += 1
        reset_flag = True
        submit_flag = False

def check_text(guess):
    '''checks if word is correct or not'''
    global word, reset_flag, submit_flag, wins
    if guess == word and submit_flag:
        print('Correct! Click the fetch button to get your next word')
        wins += 1
        reset_flag = True
        submit_flag = False
        
def check_tries():
    '''checks to see how many attempts have been made'''
    global attempts, word, reset_flag, submit_flag, losses
    if attempts == tries.value and submit_flag:
        print("You're out of tries! The correct word was: {}\nClick the fetch button to get your next word".format(word))
        losses += 1
        reset_flag = True
        submit_flag = False
        
# Gameplay        
        
def handle_submit(sender):
    '''callback function used to interact with text input from user'''
    global word, attempts, words, timer
    if submit_flag:
        if validate_guess(text.value, word, words):
            check_time()
            if submit_flag:
                give_feedback(text.value, word)
            check_text(text.value)
            attempts += 1
            check_tries()
            timer = time.time()
            
def fetch_button(sender):
    '''callback function to retrieve a new word.'''
    global reset_flag, submit_flag, word, words, fin, timer, attempts
    if reset_flag == True:
        clear_output()
        word = pick_word(curate_words(words))
        give_feedback('{}'.format(word[0]), word)
        timer = time.time()
        attempts = 0
        reset_flag = False
        submit_flag = True
        
def show_record(sender):
    '''displays wins and losses. can only be called at the end of a round.'''
    global wins, losses, submit_flag
    if not submit_flag:
        clear_output()
        print('wins: {}\nlosses:{}'.format(wins, losses))
        
def restart_game(sender):
    '''clears wins and losses'''
    global wins, losses, submit_flag, reset_flag
    wins, losses = 0, 0
    submit_flag = False
    reset_flag = True
    clear_output()
    
rules = widgets.Button(description="Instructions",
                       layout=Layout(width='15%',height='90%', right='10px'))
length = widgets.Dropdown(value=5,
                          options=[5,6,7,8],
                          continuous_update=True,
                          description='word length:')                                                                                                       
tries = widgets.Dropdown(value=5,
                         options=OrderedDict({5:5,6:6,7:7,8:8,9:9,10:10,'unlimited':math.inf}),
                         continuous_update=True,
                         description='number of attempts:')
clock = widgets.Dropdown(value=10,
                         options=OrderedDict(sorted({10:10,15:15,20:20,25:25,30:30,'unlimited':math.inf}.items(), key=lambda t: t[1])),
                         continuous_update=True,
                         description='sec per guess:')
text = widgets.Text(placeholder="Type your guess here",disabled=False)
fetch = widgets.Button(description='Fetch Word')
record = widgets.Button(description='Show Record')
restart = widgets.Button(description='Restart Game')
text.on_submit(handle_submit)
fetch.on_click(fetch_button)
rules.on_click(on_button_clicked)
record.on_click(show_record)
restart.on_click(restart_game)

# Checking guesses against the rules

def validate_guess(guess, word, words):
    '''Let's the user know if his/her guess violates the rules'''
    if len(guess) > length.value:
        print("That's too long, please try again...")
        return False
    if len(guess) < length.value:
        print("That's too short, please try again...")
        return False
    if guess not in words:
        print("That's not a valid word, please try again...")
        return False
    if guess[0] != word[0]:
        print("Check your first letter and try again...")
        return False
    else: return True
    
def tally_letters(word, guess):
    '''records the letters in the right and wrong position.  Used in conjunction with assign_colors'''
    letter_count = Counter(word)
    red, yellow = [],[]
    for (index, letter) in enumerate(guess):
        if letter == word[index]:
            red.append((index,letter))
            letter_count[letter] -= 1
    for (index, letter) in enumerate(guess):
        if letter in word and letter_count[letter] > 0:
            yellow.append((letter))
            letter_count[letter] -= 1
    return red, yellow

# Functions related to styling output

def make_yellow(c, color='black',size='12pt'):
    '''displays a yellow circle around letter if it's in the wrong position'''
    dark_yellow = '#e6b800'
    opening_tag = '''<span style="border-style: solid; border-width: 2px; border-radius: 50%; border-color: {};
    margin-right: 1px; margin-left: 1px;padding-bottom: 2px; padding-left: 9px; padding-right: 9px;color:{}; 
    font-size:{}">'''.format(dark_yellow, color, size)
    closing_tag = "</span>"
    return opening_tag + c + closing_tag

def make_red(c):
    '''displays a red square around letter if it is in the right position'''
    opening_tag = '''<span style="font-size: 12pt; border-style: solid; border-color: red; padding-left: 9px;
    padding-right: 9px; padding-bottom: 2px; border-width: 2px; margin-left: 1px; margin-right: 1px;color: black">'''
    closing_tag = '</span>'
    return opening_tag + c + closing_tag

def make_blank(c):
    '''a blank background to show around bad letters, used to make spacing even'''
    opening_tag = '''<span style="font-size: 12pt; border-style: solid; border-color: white; padding-left: 9px;
    padding-right: 9px;border-width: 2px; margin-left: 1px; margin-right: 1px;color: black">'''
    closing_tag = '</span>'
    return opening_tag + c + closing_tag

def assign_colors(guess, word, red, yellow):
    '''Applies the HTML functions to the letters determined by tally_letters'''
    feedback = ''
    letter_count = Counter(word)
    for (index,letter) in enumerate(guess):
        if (index,letter) in red:
            feedback += make_red(letter)
            letter_count[letter] -= 1
        elif letter in yellow and letter_count[letter] > 0:
            feedback += make_yellow(letter)
            letter_count[letter] -= 1
        else:
            feedback += make_blank(letter)
    return feedback

def assign_colors(guess, word, red, yellow):
    '''Applies the HTML functions to the letters determined by tally_letters'''
    feedback = ''
    letter_count = Counter(word)
    for (index,letter) in enumerate(guess):
        if (index,letter) in red:
            feedback += make_red(letter)
            letter_count[letter] -= 1
        elif letter in yellow and letter_count[letter] > 0:
            feedback += make_yellow(letter)
            letter_count[letter] -= 1
        else:
            feedback += make_blank(letter)
    return feedback

def give_feedback(guess, word):
    '''function used to provide the user with feedback'''
    red, yellow = tally_letters(word, guess)
    feedback = assign_colors(guess, word, red, yellow)
    display(HTML(feedback))    