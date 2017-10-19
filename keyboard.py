
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
from preferences import pref
from gpstrack import *
from foodapi import *

bot = telepot.Bot('406130496:AAFNc17PwDi7mmsYVAg2bYBtsc1LR1OlqVg')

#handling keyboards in telegram bot
class keyboard :    
#remove the existing custom keyboard , then create a custom keyboard of 2 choices ( choice1 and choice2 ), then send it together with a message to the given chat id .
  def customkeyboard(choice1 , choice2 , chat , chat_id) :
    markup = ReplyKeyboardRemove()
    bot.sendMessage(chat_id, 'Oke lah, got it!', reply_markup=markup)
    markup = ReplyKeyboardMarkup(keyboard=[[ choice1 , KeyboardButton(text= choice2 )],], resize_keyboard=True)         
    bot.sendMessage(chat_id, chat, reply_markup=markup)
       
#remove the existing custom keyboard , then create a custom keyboard of 3 choices ( choice1 , choice2 , choice3 ), then send it together with a message to the given chat id .
  def customkeyboard3(choice1 , choice2, choice3 , chat , chat_id) :
      
    markup = ReplyKeyboardRemove()
    bot.sendMessage(chat_id, 'Oke lah, got it!', reply_markup=markup)
    markup = ReplyKeyboardMarkup(keyboard=[[ choice1 , choice2,], 
                                              [choice3],], resize_keyboard=True)
               
    bot.sendMessage(chat_id, chat, reply_markup=markup)        
    
#listx is a list of string . Create an inline query , with choices are the first 10 string elements in listx , then send it together with a chat to the given chat id .
  def inlinequery10(chatid , listx , chat ) :
    all = []
    for i in listx[:10]: #Only take first 10 top results (not to spam the bot chat)
      element = [InlineKeyboardButton(text=  i , callback_data = i)]
      all.append(element)
    keyboard = InlineKeyboardMarkup(inline_keyboard= all)
    bot.sendMessage(chatid , chat , reply_markup=keyboard)
        
#listx is a list of string . Create an inline query , with choices are strings in listx , then send it together with a chat to the given chat id .
 
  def inlinequery(chatid , listx , chat ) :
    all = []
    for i in listx: 
      element = [InlineKeyboardButton(text=  i , callback_data = i)]
      all.append(element)
    keyboard = InlineKeyboardMarkup(inline_keyboard= all)
    bot.sendMessage(chatid , chat , reply_markup=keyboard)

#Check if there is an error from the api call
  def check_error(checker, chat_id):
    if (isinstance(checker,dict)):
      if (list(checker)[0] == "Error"):
        return checker["Error"]
      elif (list(checker[chat_id])[0] == "Error"):
        return checker[chat_id]["Error"]
      else:
        return 0
    else:
        return 0
#remove the current custom keyboard from the chat with the given chat id        

  def remove_custom(chat_id) :
    markup = ReplyKeyboardRemove()
    bot.sendMessage(chat_id, 'Oke lah , got it !', reply_markup=markup)
#check whether a string is in a list and return the order of the string in the list 

  def list_order (string , listt) :
    count = 0
    for i in listt :
      count += 1
      if string == i :
        break
    return (count)
#correct the string x such that : + No spaces at the start or end of the string 
#                                 + Each word is seperated by EXACTLY ONE space . 
#                                 + Every word has its first letter written in upper case .            
        
  def correction(x) :
    if len(x) == 1 :
      return (False)
    x = x.lower()
    last = len(x)-1
    first_space = 0
    for i in range( 0 , last+1) :
      if x[i] == " " :
        first_space += 1 
      else :
        break
    x = x[first_space:]
   
    last = len(x) -1
    last_space = 0
    for i in range (0 , last+1):
      j = -i-1
      if x[j] == " " :
        last_space += 1 
      else :
        break
    x = x[:last-last_space+1]
    x = x.lower()
    last = len(x)-1
    viethoa = x[0].upper()
    x = viethoa + x[1:]
    
    raw = x
    for i in range(0,last+1) :
      if i > len(x)-1 :
        break  

      if x[i] == " " :
        count = 0
        for j in range ( i+1 , last + 1):
          if x[j] == " " :
            count +=1
          else :
            break
        x = x[:i+1] + x[i+count+1:]
      
      last = len(x)-1
      for i in range ( 1 ,last-1) :
        if x[i] == " " :
          viethoa = x[i+1].upper()
          x = x[:i+1] + viethoa + x[i+2:]
      
      if x[-2] == " " :
        x = x[:last] + x[-1].upper()
    
    return(x)

#Handling miscellaneous repetitive tasks in telegram bot, the bridge between outputs of api platforms (Recipe api/ direction api) and chat messages in bot
class api_to_bot:
  #Allow users to search individual info of each dish in the result list. To minimize API Call per search, we save the entire search result of each user in the collated dictionary results_list. 
  #When the user need pieces of info, we do not need to perform another API call but to fetch it in results_list. 
  #The dictionary is stored in the program itself in stead of writing in an external file so as to speed up the read and write process.     
  def recipe_handler(checker, from_id):
    if keyboard.check_error(checker, from_id) == 0:
      pref.keyin = food_api.search_chat_id(from_id,results_list,1)
      keyboard.inlinequery10(from_id , pref.keyin, "Here are most relevant the recipes ! (Hint: you can go back to this message if you want to find out more about other dishes; or type /mydisheslist)")  
    
    #Edge case when the API Call return an error. Notify the user (No result from the search, API Call limit reached, Other external errors...)
    else:        
      bot.sendMessage(from_id , keyboard.check_error(checker, from_id))  
  
  #send a location request to the given chat id
  def location(chat_id) :
    markup = ReplyKeyboardRemove()
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Sure! Send My Location',request_location=True)]], resize_keyboard=True, one_time_keyboard=True)
    bot.sendMessage(chat_id, 'Give location?', reply_markup=keyboard)
  
  #handling tasks after user's location is sent
  def get_user_location(from_id, msg):
    bot.sendMessage(from_id, "Thanks for sharing your location ☺")
    pref.user_location = str(msg['location']['latitude']) + "," + str(msg['location']['longitude'])  

  def get_direction(from_id, canteen_name):
       destination = google_maps.canteen_latlng("PlaceID.xlsx", "placeid", canteen_name)
       google_maps.new_id(from_id, chat_id_list_dir)
       #Find direction with Google Maps API and print out the direction instructions + estimated distance
       checker = google_maps.direction(from_id, chat_id_list_dir, results_list_dir, pref.user_location, destination)
       if keyboard.check_error(checker, from_id) == 0:
          instructions = google_maps.direction_instructions(from_id, results_list_dir)
          distance = google_maps.calculate_distance(from_id, results_list_dir)
          bot.sendMessage(from_id,"Here are the instructions " + canteen_name + ":")
          if isinstance(instructions, list): #check for []
              bot.sendMessage(from_id , '\n'.join(str(x) for x in instructions)) 
          else:
              bot.sendMessage(from_id , ' '.join(str(x) for x in instructions))     
          bot.sendMessage(from_id,"Estimated distance: "+ str(distance))     #Send the statics map snapshot of the location using Google Maps API
          google_maps.get_photo(destination)
          bot.sendPhoto(chat_id=from_id, photo=open('phototestt1.jpeg', 'rb'))
          bot.sendMessage(from_id,"Hope you won't get lost! Please type 'eatntu' or '/eatntu' to restart")  

       else:
          bot.sendMessage(from_id , keyboard.check_error(checker, from_id)) 

        

    
 

