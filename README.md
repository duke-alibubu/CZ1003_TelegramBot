# chipsmore
---------------------------------------------------------Team ChipsMORE!------------------------------------------------------------
Team Member : Trinh Tuan Dung 
              Dinh Khoat Hoang Anh
              Nguyen Ngoc Khanh
              Fransiscus Xaverius Wilbert
              Stella Marcella Lie
Bot Name : eatNTU (@eat_NTUbot)

Description of files :


- main.py : Main Python file to run .
- keyboard.py :  create custom keyboards & inline queries , correct user's typing errors ; as well as acting as a bridge between outputs of API platforms and chat messages in bot .
- chat_history.py : This file saves chat history for some purposes of Eat In.
- database.txt : This file saves chat history for further purposes.
- credentialshhanh.py : save API keys and URL links to call API platform .
- foodapi.py : call recipes using API platform " Yummly " (In case Yummly API calls runs out , use "Food2Fork" and "RecipePuppey" API platform ).
- gpstrack.py : call direction instructions , calculate distances & call statics map using API platform "Google Maps".
- phototest.JPEG : temporarily store statics map image to be sent to users . 
- preferences.py : store global variables to be modified in main.py's functions , such as user's preference and indexes .
- Procfile.py : for Heroku .  
- requirements.txt : for Heroku .
- xl.py : read , write and process the Excel file .
- Canteen Restaurant List .xlsx : A Excel file that contains various sheets . Each sheet is about a single canteen in NTU  :
     + Column C contains the names of each stalls in the canteen. 
     + Column B contains the types of stalls.
     + Column D contains the names of the dishes in the stalls.
     + Column E contains the prices of the dishes.
     + Column F indicates whether a dish is healthier or not.
 Our eatNTU bot can access this Excel file to give out the names of canteens , or information about the stalls and the prices of dishes , as well as an addtional indication whether a dish is healthy . 

- PlaceID.xlsx : A Excel file that indicates the locations of NTU canteens :
     + Column A contains the names of canteens.
     + Column B indicates the place ID of canteens.
     + Column C indicates the addresses of canteens.
     + Column D and column E respectively indicates the latitudes and longtitudes of canteens. 
 To save the number of API calls ( because it is limited ) we make it an offline database . And this will make the locations more standardized and error - free .
 




                                
