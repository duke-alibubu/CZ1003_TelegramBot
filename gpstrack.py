from googlemaps import Client as GoogleMaps
import requests
import json
import re
from PIL import Image

import math

# API Call destinations and key
from credentialshhanh import *
from xl import *

results_list_dir = {}
chat_id_list_dir = []

class google_maps:
  #Read file from excel to convert to list of canteens in python
  def excel_to_list(file, ws_name):
    ws = xl.load_ws(xl.load_wb(file), ws_name)
    place_list = []  
    for i in range(2,len(ws["A"])+1):
      place_list.append(xl.cell(ws, "A" + str(i)))
    return place_list  
  
  #Read file from excel to convert to dictionary of canteens and their respective lat lng in python
  def excel_to_dict(file, ws_name):
    ws = xl.load_ws(xl.load_wb(file), ws_name)
    place_list = {}  
    for i in range(2,len(ws["A"])+1):
      canteen = xl.cell(ws, "A" + str(i))
      lat_lng = google_maps.canteen_latlng(file, ws_name, canteen)
      place_list[canteen] = lat_lng
    return place_list  
  
  #Read canteen lat lng from the file
  def canteen_latlng(file, ws_name, canteen):
    ws = xl.load_ws(xl.load_wb(file), ws_name)
    canteen_latlng = str(xl.cor_content(ws, "A", "D",canteen)) + "," + str(xl.cor_content(ws, "A", "E",canteen))  
    return canteen_latlng  
  
  #Register new user on the results_list_dir
  def new_id(chat_id_dir, chat_id_list_dir):
    chat_id_list_dir = google_maps.check_overlapping_id(chat_id_dir, chat_id_list_dir, results_list_dir)
    chat_id_list_dir.append(chat_id_dir)
    return chat_id_list_dir  
  
  #Make sure that one user can only make one API call at any time
  def check_overlapping_id(chat_id_dir, chat_id_list_dir, results_list_dir):
    for i in chat_id_list_dir:
      if i == chat_id_dir:
        print("Your old search is deleted.")
        chat_id_list_dir, results_list_dir = google_maps.delete_id(chat_id_dir, chat_id_list_dir, results_list_dir)
    return chat_id_list_dir  
  
  #Delete old API call of the user (if one has)
  def delete_id(chat_id_dir, chat_id_list_dir, results_list_dir):
    chat_id_list_dir.remove(chat_id_dir)
    del results_list_dir[chat_id_dir]
    return (chat_id_list_dir, results_list_dir)
  
  #Call API from googlemaps
  def fetch_data(search_payload, url, mode):
    if mode == 0:
      search_req = requests.get(url, params=search_payload)
      data = search_req.json()    
      if data["status"] == "OK":      
        return data		  
      elif data["status"] == "OVER_QUERY_LIMIT":
        print("Exceed rate limit! Contact your admin")
        return {"Error": "Exceed rate limit! Contact your admin"}
        exit()	  
      else:
        print("Error!")
        return {"Error": "API Error!"}
        exit()  
    elif mode == 1:
      search_req = requests.get(url, params=search_payload, stream=True)
      data = Image.open(search_req.raw).convert('RGB')
      data.save('phototest.jpeg', "JPEG")
      return data  
  #Find direction with googlemaps (origin and direction in lat,lng) (default by driving - it is quite close to walking direction in NTU context, and this is more useful than walking search mode even when the user's location is very far away from the canteens)
  def direction(chat_id_dir, chat_id_list_dir, results_list_dir, origin, destination):
    #Get direction
    search_payload = {"origin": origin, "destination": destination, "key": google_key}
    results_list_dir[chat_id_dir] = google_maps.fetch_data(search_payload, direction_url, 0)
    return results_list_dir  
  #Refine the direction instructions
  def direction_instructions(chat_id_dir, results_list_dir):
    # Extract and print the direction instructions
    instructions = []
    for i in range (0, len (results_list_dir[chat_id_dir]['routes'][0]['legs'][0]['steps'])):
      j = results_list_dir[chat_id_dir]['routes'][0]['legs'][0]['steps'][i]['html_instructions']
      if '<div style="font-size:0.9em">' in j: #Special case in API Google Maps Call
        j = j.replace('<div style="font-size:0.9em">', '\n')
      clean_j =  re.sub('\<.*?\>', '', j)
      instructions.append(clean_j)
    return instructions	
  
  #Calculate ROUTE distance with googlemaps
  def calculate_distance(chat_id_dir, results_list_dir):
  	#calculate distance between 2 places
  	distance = results_list_dir[chat_id_dir]['routes'][0]['legs'][0]['distance']['text']
  	return distance	  
  #Calculate STRAIGHT LINE distance with formula calculation, this is to save the number of API calls to googlemaps (due to limited number of API calls)
  def haversine_distance(point1, point2):
    """
    # original formula from  http://www.movable-type.co.uk/scripts/latlong.html 
    Haversine formula: 
        a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
                        _   ____
        c = 2 ⋅ atan2( √a, √(1−a) )
        d = R ⋅ c	  
    where φ is latitude, λ is longitude, R is earth’s radius (mean radius = 6,371km);
            note that angles need to be in radians to pass to trig functions!	  
    :p1:     (tup) lat,lon
    :p2:     (tup) lat,lon
    """
    lat1, lng1 = float(point1.split(',')[0]), float(point1.split(',')[1])
    lat2, lng2 = float(point2.split(',')[0]), float(point2.split(',')[1])  
    R = 6371.0 # km - earths's radius	  
    # convert decimal degrees to radians 
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])	  
    # haversine formula 
    dlng = lng2 - lng1
    dlat = lat2 - lat1	  
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d	  
  #Sort the canteens in the order of increasing distance based on the user's location
  def sort_nearby_place(origin_lat_lng, file, ws_name):  
  	place_list = google_maps.excel_to_dict(file, ws_name)  
  	distance_list = []
  	for place in place_list.items():
  		place_name = place[0]
  		destination_lat_lng = place[1]
  		straight_distance = google_maps.haversine_distance(origin_lat_lng, destination_lat_lng)
  		distance_list.append(straight_distance)	  
  	sorted_place_list = [j for i,j in sorted(zip(distance_list, place_list))]
  	return sorted_place_list  
  #return photo of a canteen  
  def get_photo(destination_latlng):
  	search_payload = {"center": destination_latlng, "zoom": "17", "size": "400x400", "key": google_key}
  	
  	data = google_maps.fetch_data(search_payload, map_url, 1)
  	return data


