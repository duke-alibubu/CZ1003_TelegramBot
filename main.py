import telepot 
from telepot.loop import MessageLoop
import time
import datetime
import random
from credentialshhanh import *
from foodapi import *
from keyboard import *
from chat_history import chat_history
from xl import xl
from preferences import pref
from gpstrack import *
'''
Intruction: type eatntu to restart the bot
'''
bot = telepot.Bot('406130496:AAFNc17PwDi7mmsYVAg2bYBtsc1LR1OlqVg')
result_list ={}
chat_id_list =[]

#Recipe Info headings for API CALL
headers_puppy = {0: "Puppy's Recipe directions", 1: "Puppy's Ingredients", 2: "Puppy's Image"}
headers_food2fork = {0: "Food2fork's Recipe directions", 1: "Food2fork's Image", 2: "Food2fork's Ingredients and Nutrition Facts", 3: "Food2fork's Rating"}
headers_yummly = ["Yummly's Recipe directions", "Yummly's Image", "Yummly's Ingredients", "Time needed (seconds)", "Yummly's Rating (out of 4)"]

#List types of food (only for Yummly)
type_options =['American', 'Italian', 'Asian', 'Mexican', 'French', 'Southwestern', 'Barbecue', 'Indian', 'Chinese', 'English', 'Mediterranean', 'Greek', 'Spanish', 'German', 'Thai', 'Moroccan', 'Irish', 'Japanese', 'Cuban', 'Hawaiin', 'Swedish', 'Hungarian', 'Portugese']
diet_options =['Pescetarian', 'Vegan', 'Vegetarian']

#The location, latitude and longtitude of Food locations are pre-set to avoid users's spamming the direction. In addition, it will save no. of API Call from Google Maps in subsequent operations
canteen_location_list = google_maps.excel_to_list("PlaceID.xlsx", "placeid")



#Advertisment for our group name. The probablity of displaying the ad is 40% when the function is called
def voting_ad(msg):
  content_type, chat_type, chat_id = telepot.glance(msg)
  data = [0]*6 + [1]*2 + [2]*2
  #Advertisment varies to avoid repetition 
  if (random.choice(data) == 1):
    bot.sendMessage(chat_id, '☕ WHEAT a second… Vote for team ChipsMORE! if you like our bot!!!')
  elif (random.choice(data)) == 2:
    bot.sendMessage(chat_id, 'By the way, CHIPZ in a VOTE for team ChipsMORE! (｡◕‿◕｡)')


#Cases for messages received
def on_chat_message(msg):
  content_type, chat_type, chat_id = telepot.glance(msg)
 
  #If the message is the location user sent
  if content_type == 'location' :
    api_to_bot.get_user_location(chat_id, msg)
    if  chat_history.lastest_message0(chat_id) == "search for direction" or chat_history.lastest_message0(chat_id) == '/searchfordirection' :
  	  keyboard.inlinequery(chat_id , canteen_location_list + ["Canteen nearest me!"], ' Choose your canteen ! ')
    elif chat_history.lastest_message0(chat_id) == "How to get there?":
  	  api_to_bot.get_direction(chat_id, "to " + pref.canteen_name[chat_id])
 
  #If the message is the chat text
  elif content_type == 'text' :    
    chat_history.write_data(chat_id, msg['text'].lower())
    #Check edge cases when the user type spam messages
    if (keyboard.correction(msg['text']) not in ["Eatntu" , "/eatntu" , "Eat Ntu" , "Eat Out" , "/eatout" , "/eatin" , "Eat In" , "Dish Name" , "Ingredient" , "Give location ?", "How to get there?", "Search For Direction", "/searchfordirection", "Canteen nearest me!", "/searchdirection" , "/start","/mydisheslist", "My Dishes List","Food Type"] and chat_history.lastest_message1(chat_id)  not in ["dish name" , "ingredient"]) and chat_history.lastest_message2(chat_id)  not in ["ingredient"] or keyboard.correction(msg['text']) == False :
      bot.sendMessage(chat_id , "Oops you have typed in the wrong syntax . Please type 'eatntu' or '/eatntu' to restart")
    #Response for /start
    if keyboard.correction(msg['text']) == '/start' :
      bot.sendMessage(chat_id , " Hello and welcome to @eat_NTUbot ! Let's eat the whole NTU together , I mean , eat the food in NTU . Now to start , please type '/eatntu' or 'Eat NTU' !")
    #Response for /eatNTU with its recognisable variations    
    if keyboard.correction(msg['text'])  == 'Eatntu' or keyboard.correction(msg['text']) == 'Eat Ntu' or msg['text'] == '/eatntu':
      keyboard.customkeyboard3('Eat Out' , 'Eat In ', 'Search For Direction', "let's see what u want to do", chat_id)
      #Message to ask for voting
      voting_ad(msg)

###### EAT IN #####
  #Response for /eatin with its recognisable variations 
  if keyboard.correction(msg['text']) == 'Eat In' or msg['text'] == "/eatin" :
    keyboard.customkeyboard3('Dish Name' , 'Ingredient' , "Food Type", "What do you want to search the recipe by?",chat_id)
  
  #Response when the user want to search recipes by dish name with its recognisable variations 
  if keyboard.correction(msg['text']) =='Dish Name' :
    keyboard.remove_custom(chat_id)
    bot.sendMessage(chat_id, 'Key in the dish name:')
  
  #Response when the user want to search recipes by ingredients with its recognisable variations 
  if keyboard.correction(msg['text']) =='Ingredient' :
    keyboard.remove_custom(chat_id)
    bot.sendMessage(chat_id, 'Key in the ingredients, seperated by comas :')
  #Response after user keys in the ingredients he/she wants
  if chat_history.lastest_message1(chat_id) =='ingredient':
    bot.sendMessage(chat_id, 'Key in the ingredients you DONT WANT, seperated by comas (Psst.. if you dont have this, type Nil):')
  
  #Response when the user want to search recipes by food type with its recognisable variations
  if keyboard.correction(msg['text']) =='Food Type':
    keyboard.remove_custom(chat_id)
    keyboard.inlinequery(chat_id, type_options + diet_options, 'Which food type are you looking for?')
  
  #Search for recipe with dish name's keywords
  if chat_history.lastest_message1(chat_id) =='dish name' :
    food_api.new_id(chat_id,chat_id_list)
    #Search based on Yummly search (in case of the API Call Limit reaches, we will switch to Food2Fork)
    checker = food_api.yummly_search(chat_id,chat_id_list,results_list,msg['text'].lower(), None, None, None)
    api_to_bot.recipe_handler(checker, chat_id)
  
  #Search for recipe with ingredient's keywords (register ingredients wanted) 
  if chat_history.lastest_message1(chat_id) =='ingredient' :
    pref.ingredient = msg['text']

  #Search for recipe with ingredient's keywords (register ingredients NOT wanted)  
  #Search based on Yummly search (in case of the API Call Limit reaches, we will switch to Recipe Puppy) - Recipe Puppy does not have excluded ingredients feature so we will disable this part
  if chat_history.lastest_message2(chat_id) =='ingredient' :
    food_api.new_id(chat_id,chat_id_list)

    #If the user do not want to exclude any ingredients
    if keyboard.correction(msg['text']) == 'Nil':
      msg['text'] = " "
    
    checker = food_api.yummly_ing_search(chat_id,chat_id_list,results_list, None, pref.ingredient, msg['text'], None)
    api_to_bot.recipe_handler(checker, chat_id)

  #Print out the lastest list of dishes searched by the user
  if keyboard.correction(msg['text']) == 'My Dishes List' or msg['text'] == '/mydisheslist' :      
    keyboard.inlinequery10(chat_id , pref.keyin, "Here are your last list of recipes ! (again)")
  
  #Response for /eatout with its recognisable variations 
  if keyboard.correction(msg['text']) == 'Eat Out' or msg['text'] == "/eatout" :
    #Clean last eat-out data of a user if they type Eat Out
    pref.user_type[chat_id] = ''
    pref.canteen[chat_id] = ''
    pref.canteen_name[chat_id] = ''
    pref.stall[chat_id] = ''
    pref.food_type[chat_id] = ''

    keyboard.inlinequery(chat_id, ['A Random Dish','A Food Type','A Canteen'], 'What do you want to search?')
  
  #Response for /searchfordirection with its recognisable variations 
  if keyboard.correction(msg['text']) == 'Search For Direction' or msg['text'] == "/searchfordirection":
    api_to_bot.location(chat_id)
  
  ###################################
  #Record chat history (text message) in database for tracking
  chat_history.export_data(chat_id, msg['text'])


#Cases for query received
def on_callback_query(msg): 
  query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
 
  #Record chat history (inlinequery) for corresponding interaction with other user
  chat_history.write_data(from_id,query_data)
  ###################################
  #Record chat history (inlinequery) in database for tracking
  chat_history.export_data(from_id,query_data)

  #If the query data is in the food type list (When the user chooses to search by food type)
  for i in type_options + diet_options:
    if query_data == i:
      food_api.new_id(from_id, chat_id_list)
      checker = food_api.yummly_type_match(from_id, chat_id_list, results_list, query_data)
      api_to_bot.recipe_handler(checker, from_id)
      pass 

  #If the query data is in the list of dishes searched by the user
  for i in pref.keyin :
    if query_data == i :
      pref.recipeindex = keyboard.list_order( i , pref.keyin)
      keyboard.inlinequery10(from_id , list(headers_yummly) , " What do u want to see about " + i + "?" )
      pass 

  #If the query data is in the list of info for food API 
  for i in headers_yummly:
    if query_data == i :
      data_index = keyboard.list_order(query_data, headers_yummly)
      checker = food_api.search_chat_id(from_id, results_list, 2, pref.recipeindex-1, data_index)

      if keyboard.check_error(checker, from_id) == 0:
        if isinstance(checker, list): #Check for first []
        	if isinstance(checker[0], list): #check for second []
        		bot.sendMessage(from_id , i + ": " + ', '.join(str(x) for x in checker[0]))
        	
        	else:
        		bot.sendMessage(from_id , i + ": " +' '.join(str(x) for x in checker))
        else:
        	bot.sendMessage(from_id , i + ": " +checker)
      else:
        bot.sendMessage(from_id , keyboard.check_error(checker, from_id)) 
      pass 

 ###### DIRECTION #####
  #When user wants to find direction to a certain food location
  for i in canteen_location_list :
      if query_data == i :
      	 api_to_bot.get_direction(from_id, query_data)
      pass   
  #Sort the food locations from nearest to furthest in straight-line distance in relation to the user's current location
  #We used straight-line distance instead of Google Maps's route distance in order to save significant number of API Call 
  #(Google API has limited API call rate, so this function will be more reliable when the users traffic is high)
  if query_data == "Canteen nearest me!":
   	keyboard.inlinequery(from_id, google_maps.sort_nearby_place(pref.user_location, "PlaceID.xlsx", "placeid"), "✌ Food places listed from nearest to furthest for you...")
   	pass
  if query_data == "How to get there?":
  	api_to_bot.location(from_id) 


###### EAT OUT #####
#Load file excel to variable 'wb'
  wb = xl.load_wb('Canteen Restaurant List.xlsx')



#USER CHOOSES A RANDOM DISH
  if query_data == 'A Random Dish' or query_data == 'Re-random a dish':
    #randomize a canteen
    pref.canteen_name[from_id] = str(random.choice(xl.sheets(wb)))
    canteen = wb[pref.canteen_name[from_id]]
    #randomize a dish in the canteen
    dish_name = str(random.choice(xl.column(canteen, 'D')))
    price = str(xl.cor_content(canteen,'D','E', dish_name))
    stall = str(xl.stall(canteen, 'D', 'C', dish_name))
    dish_msg = "✌ Join 'ChipsMORE! the Explorer' eating:\n" + dish_name +', for $'+price+' at '+stall +' in '+ pref.canteen_name[from_id]
    #send message
    keyboard.inlinequery(from_id, ['How to get there?', 'Re-random a dish'], dish_msg)
    bot.sendMessage(from_id, "Or.. if you are satisfied, Please type 'eatntu' or '/eatntu' to restart")



#USER CHOOSES A FAVORITE FOOD TYPE
  if query_data == 'A Food Type':
    #write user type
    pref.user_type[from_id] = 'A Food Type'
    #send message
    keyboard.inlinequery(from_id, xl.all_columns(wb, 'B'), 'Choose your food type:')
  #if user is "A Food Type" type and they chose a food type then
  if (query_data in xl.all_columns(wb, 'B')) and pref.user_type[from_id] == 'A Food Type':
    #write food type
    pref.food_type[from_id] = query_data
    #send message stalls in the canteen
    keyboard.inlinequery(from_id, xl.stall_and_sheet(wb, 'B', 'C', pref.food_type[from_id]), 'Here are the stalls')
  #if user chose the string contains canteen name and stall.
  if query_data in xl.stall_and_sheet(wb, 'B', 'C', pref.food_type[from_id]):
    #write stall name
    pref.stall[from_id] = query_data.split(' in ')[0]
    #write canteen name
    pref.canteen_name[from_id] = query_data.split(' in ')[1]
    pref.canteen[from_id] = wb[pref.canteen_name[from_id]]
    #send message
    keyboard.inlinequery(from_id, ['All dishes', 'Healthier choices', 'How to get there?'], 'You did choose '+ query_data)

   
#USER CHOOSES A CANTEEN
  if query_data == 'A Canteen':
    #write user type as "A Canteen"
    pref.user_type[from_id] = 'A Canteen'
    #send the list of canteens
    keyboard.inlinequery(from_id, xl.sheets(wb), 'Choose one:')

  #if user chose a canteen
  if (query_data in xl.sheets(wb)) and (pref.user_type[from_id] == 'A Canteen'):
    #write canteen
    pref.canteen_name[from_id] = str(query_data)
    pref.canteen[from_id] = xl.load_ws(wb, str(query_data))
    #send message list of stalls in the canteen
    keyboard.inlinequery(from_id, xl.column(pref.canteen[from_id], 'C'), 'You did choose '+ pref.canteen_name[from_id] +', choose a stall')

  #if user type is "A canteen" and they chose 1 stall
  if (query_data in xl.column(pref.canteen[from_id], 'C')) and (pref.user_type[from_id] == 'A Canteen'):
    #write stall name
    pref.stall[from_id] = str(query_data)
    #send message
    keyboard.inlinequery(from_id, ['All dishes', 'Healthier choices', 'How to get there?'], 'You did choose '+ query_data)



#READY TO SEND DISHES TO USER
  #if user chose to print all dishes
  if query_data == 'All dishes':
    #calculate the begining row and the end row for a stall
    row1 = xl.row(pref.canteen[from_id], 'C', pref.stall[from_id])
    row2 = xl.next_row(pref.canteen[from_id], 'C', 'E', pref.stall[from_id])
    #initialize the message out and send
    message_out = ''
    for i in range(row1, row2):
      message_out = message_out + str("★ " + pref.canteen[from_id]['D'][i].value) + ', $' + str(pref.canteen[from_id]['E'][i].value) + '\n'
    bot.sendMessage(from_id, message_out)
    bot.sendMessage(from_id, "Please type 'eatntu' or '/eatntu' to restart")
  #the same as "All dishes"
  if query_data == 'Healthier choices':
    row1 = xl.row(pref.canteen[from_id], 'C', pref.stall[from_id])
    row2 = xl.next_row(pref.canteen[from_id], 'C', 'E', pref.stall[from_id])
    message_out = ''
    for i in range(row1, row2):
      if pref.canteen[from_id]['F'][i].value != None:
        message_out = message_out + str("★ " + pref.canteen[from_id]['D'][i].value) + '\n'
    if message_out == '':
      bot.sendMessage(from_id, 'Sorry, this stall has no healthier choice.')
    else:
      bot.sendMessage(from_id, message_out)
    bot.sendMessage(from_id, "Please type 'eatntu' or '/eatntu' to restart")

     
  bot.answerCallbackQuery(query_id, text='Got it...')

     
    
 


MessageLoop(bot, {'chat': on_chat_message, 
                  'callback_query': on_callback_query}).run_as_thread()


print ('Listening')
while 1 :
    time.sleep(1) 
