#version for bot10/7

import requests
import json
import re

from credentialshhanh import *
type_options =['American', 'Italian', 'Asian', 'Mexican', 'French', 'Southwestern', 'Barbecue', 'Indian', 'Chinese', 'English', 'Mediterranean', 'Greek', 'Spanish', 'German', 'Thai', 'Moroccan', 'Irish', 'Japanese', 'Cuban', 'Hawaiin', 'Swedish', 'Hungarian', 'Portugese']
diet_options =['Pescetarian', 'Vegan', 'Vegetarian']


results_list = {}
chat_id_list = []

class food_api(object):
    #Global variable for the class

    no_result = "That's a typo!! Please type 'eatNTU' to restart!"

    #List (2): Info for each recipe name - differs in various API platform
    headers_puppy = {0: "title", 1: ["href", "Recipe directions"], 2: ["ingredients", "Ingredients"], 3: ["thumbnail", "Image"]}
    headers_food2fork = {0: "title", 1: ["source_url", "Recipe directions"], 2: ["image_url", "Image"], 3: ["f2f_url","Ingredients and Nutrition Facts"], 4: ["social_rank","Rating"]}
    headers_yummly = {0: "recipeName", 1: ["id","Recipe directions"], 2: ["smallImageUrls","Image"], 3: ["ingredients","Ingredients"], 4: ["totalTimeInSeconds","Time needed (seconds)"], 5: ["rating","Rating"]}

    recipe_item_yummly = headers_yummly[0]
    api_item_yummly = "matches"
    recipe_item_puppy = headers_puppy[0]
    api_item_puppy = "results"
    recipe_item_food2fork = headers_food2fork[0]
    api_item_food2fork = "recipes"

    #Register new user on the results_list
    def new_id(chat_id, chat_id_list):
        chat_id_list = food_api.check_overlapping_id(chat_id, chat_id_list, results_list)
        chat_id_list.append(chat_id)
        return chat_id_list

    #Make sure that one user can only make one API call at any time
    def check_overlapping_id(chat_id, chat_id_list, results_list):
        for i in chat_id_list:
            if i == chat_id:
                print("Your old search is deleted.")
                chat_id_list, results_list = food_api.delete_id(chat_id, chat_id_list, results_list)
        return chat_id_list

    #Delete old API call of the user (if one has)
    def delete_id(chat_id, chat_id_list, results_list):
        chat_id_list.remove(chat_id)
        del results_list[chat_id]
        return (chat_id_list, results_list)


    ## API Call function
    def fetch_data(search_payload, url):
        search_req = requests.get(url, params=search_payload)
        
        
        if search_req.status_code == requests.codes.ok:
            data = search_req.json()        
            return data
        elif search_req.status_code == (403 or 409):
            print("Exceed rate limit! Contact your admin")
            return {"Error": "Exceed rate limit! Contact your admin"}
            exit()
        
        else:
            print("Error!")
            return {"Error": "API Error!"}
            exit()

    #Function to indicate which API platform the search is sourced from 
    def check_api_platform(platform_indicator):
        if platform_indicator == "yummly":
            api_item, recipe_item = food_api.api_item_yummly, food_api.recipe_item_yummly
        elif platform_indicator == "food2fork":
            api_item, recipe_item = food_api.api_item_food2fork, food_api.recipe_item_food2fork
        elif platform_indicator == "puppy":
            api_item, recipe_item = food_api.api_item_puppy, food_api.recipe_item_puppy


    #extract relevant data from the API call
    def search_chat_id(chat_id, results_list, mode, recipe_index=None, data_index=0): 
        #check api platform used for each chat_id search
        indicator = results_list[chat_id][0]

        if indicator == "yummly":
            heading, api_item, recipe_item = food_api.headers_yummly[data_index][0], food_api.api_item_yummly, food_api.recipe_item_yummly
        elif indicator == "food2fork":
            heading, api_item, recipe_item = food_api.headers_food2fork[data_index][0], food_api.api_item_food2fork, food_api.recipe_item_food2fork
        elif indicator == "puppy":
            heading, api_item, recipe_item = food_api.headers_puppy[data_index][0], food_api.api_item_puppy, food_api.recipe_item_puppy
        else:
            return {"Error": food_api.no_result}

        #mode 1 = list all recipe names found from the API call
        if mode == 1:
            output_list = []

            if results_list[chat_id] != food_api.no_result:
                for item in results_list[chat_id][1][api_item]:
                    output_list.append(item[recipe_item].strip())
                return output_list
            else:
                print(food_api.no_result)
                return {"Error": food_api.no_result}

        #mode 2 = list details according to the choossen recipe name
        elif mode == 2:
            output_list = [results_list[chat_id][1][api_item][recipe_index][heading]]

            #use recipeID to search for recipe directions url --> to save one API Call from Yummly
            if (indicator == "yummly") and (data_index == 1):
                output_list = [yummly_recipe_url + results_list[chat_id][1][api_item][recipe_index][heading]]
            return output_list
        else:
            print('Out of range!')
            return {"Error": 'Out of range!'}
            exit()

    #Edge case no data found
    def data_check(data, mode):
        if ((mode == 1) and (data["count"] == 0)) or ((mode == 2) and data["results"] == []) or ((mode == 3) and data["totalMatchCount"] == 0):
            return 0
        else: 
            return 1

    #API Call food2fork for data
    def food2fork_search(chat_id, chat_id_list, results_list, query, sort=None, page=None):
        query = re.findall(r"[\w']+", query)

        search_payload = {"key":food2fork_key, "q":query, "sort":sort, "page":page}
        data = food_api.fetch_data(search_payload, food2fork_url)

        if food_api.data_check(data, 1) == 1:
            results_list[chat_id] = ["food2fork", data]
        else:
            results_list[chat_id] = {"Error": food_api.no_result}

        return results_list
        
    ##API Call recipe puppy for data
    def puppy_search(chat_id, chat_id_list, results_list, ingredients, query=None, page=None):

        ingredients = re.findall(r"[\w']+", ingredients)

        search_payload = {"q":query, "i":ingredients, "page":page}
        data = food_api.fetch_data(search_payload, puppy_url)
        if food_api.data_check(data, 2) == 1:
            results_list[chat_id] = ["puppy", data]
        else:
            results_list[chat_id] = {"Error": food_api.no_result}

        return results_list

    def yummly_ing_search(chat_id, chat_id_list, results_list, query, ingredients, non_ingredients, cuisine, diet=None, time=None):
        myingredients = ingredients
        mynoningredients = non_ingredients
        food_api.yummly_search(chat_id, chat_id_list, results_list, None, myingredients, mynoningredients, None)
        return results_list

    ##API Call recipe yummly for data
    def yummly_search(chat_id, chat_id_list, results_list, query, ingredients, non_ingredients, cuisine, diet=None, time=None):
        if ingredients != None:
            ingredients = re.findall(r"[\w']+", ingredients.lower())
            non_ingredients = re.findall(r"[\w']+", non_ingredients.lower())
        if cuisine != None:
        	cuisine = "cuisine^cuisine-" + cuisine.lower()

        search_payload = {"_app_id":yummly_id, "_app_key":yummly_key, "q":query, "allowedIngredient[]":ingredients, "allowedDiet[]":diet, "excludedIngredient[]":non_ingredients, "allowedCuisine[]":cuisine, "maxTotalTimeInSeconds":time}
        data = food_api.fetch_data(search_payload, yummly_url)
        if food_api.data_check(data, 3) == 1:
        	results_list[chat_id] = ["yummly", data]
        else:
        	results_list[chat_id] = {"Error": food_api.no_result}

        return results_list

    #API Call recipe yummly for data (3rd branch - search according to food type)
    def yummly_type_match(chat_id, chat_id_list, results_list, search_type):
        if search_type in type_options:
            food_api.yummly_search(chat_id, chat_id_list, results_list, None,None,None,search_type)
        elif search_type in diet_options:
            food_api.yummly_search(chat_id, chat_id_list, results_list, None,None,None,None,search_type)
        else:
            print("Please choose something from the list!")
            return {"Error": "Please choose something from the list!"}
            exit()

        
print("Foodapi has loaded!")
