import datetime
#This file saves chat history for some purposes of Eat In. I did make it, but dont use it anymore. I dont know why the teammates use it.
#please write the discription for it.
#K


class chat_history:

  database = {} #database (dict)
#return all chat
  def show_chat(chat_id):
   return chat_history.database[chat_id]
#return lastest message
  def lastest_message0(chat_id):
    return chat_history.show_chat(chat_id)[len(chat_history.show_chat(chat_id))-1]
  def lastest_message1(chat_id):
    return chat_history.show_chat(chat_id)[len(chat_history.show_chat(chat_id))-2]
#return lastest message 2 (the message before the lastest message)
  def lastest_message2(chat_id):
    return chat_history.show_chat(chat_id)[len(chat_history.show_chat(chat_id))-3]
#write message to database for temporary use
  def write_data(chat_id, message):
    if chat_id in chat_history.database:
      chat_history.database[chat_id] = chat_history.database[chat_id] + [message]
    else:
      chat_history.database[chat_id] = ['0',message]
#export message history permanently to a txt file for tracking
  def export_data(chat_id, message):
    databasefile = open('database.txt','a')
    databasefile.writelines(str(chat_id) + ' : ' + message + ' : ' + str(datetime.datetime.now()) + '\n')
    databasefile.close()

#SAMPLE
print('chat_history has loaded')
