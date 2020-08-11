# ==== Libraries ====
import telegram
from conf.settings import GROUP_ID, MARIANA_ID, MINHO_ID

from functools import wraps
from datetime import datetime
import os
import six

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# ===================

# ==== Global Variables ====
LIST_OF_ADMINS = [GROUP_ID, MARIANA_ID, MINHO_ID]

# ==========================

# ==== Wrappers ====
def restricted(func):
	""" @RESTRICTED(func)

		A wrapper to restrict the access of a command (or any other function) to the users
		and groups listed in the LIST_OF_ADMINS global variable.
	"""
	@wraps(func)
	def wrapped(update, context, *args, **kwargs):
		user_id = update.effective_user.id
		if user_id not in LIST_OF_ADMINS:
			print("Unauthorized access denied for {}.".format(user_id))
			return
		return func(update, context, *args, **kwargs)
	return wrapped
# --

# ===================

# ==== Functions ====
def markdownfy(sentence):
	""" S_MV2 = MARKDOWNFY(S)

		Receives a string 'S' and converts it to a form that can be parsed within the
		MARKDOWN_V2 format. The function returns the new string 'S_MV2' with special
		characters in proper Markdown sintax.
	"""
	for ch in ":().!?|-+_=":
		sentence = sentence.replace(ch, '\{0}'.format(ch))

	return sentence
# --

def getFiles(folder):
	""" FILES = GETFILES(FOLDER)

		Returns a list of strings 'FILES' containing the name of all files within a folder
		given by the relative path 'FOLDER'.
	"""
	return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
# --

def add_purchase(name, cost, type):
	""" ADD_PURCHASE(NAME,COST,TYPE)

		Enters a new entry in a COMPRAS data file. The new entry is added to the file indicated
		by the current year and month. Such file is created if still unexistent.
		The new entry is in the form
			data = {'NAME', 'COST', 'TYPE', 'DATE'}
		in which 'DATE' is the current day in DD/MM/YYYY format.
	"""

	# Auxiliary variables
	today    = datetime.today().strftime("%d/%m/%Y")
	filename = "data/compras_"+datetime.today().strftime("%Y-%m")+".csv"

	# Creates the dataframe for this new purchase
	data = {'name': name, 'cost': cost, 'type':type, 'date': today}
	new_compra_df = pd.DataFrame([data])

	# Stores this purchase in the data
	try:	# If the file exists
		compras_df = pd.read_csv(filename)									# Opens the current file
		compras_df = compras_df.append(new_compra_df, ignore_index=True)	# Appends the new entry to the dataframe
		compras_df.to_csv(filename, index=False)							# Re-writes the dataframe to the file

	except FileNotFoundError: # If the file does not exists
		new_compra_df.to_csv(filename, index=False) 						# Creates a new file with only the new entry
# --

def render_table(data, col_width=3.0, row_height=0.625, font_size=14, header_color='#40466e', row_colors=['#f1f1f2', 'w'],
					edge_color='w', bbox=[0, 0, 1, 1], header_columns=0, ax=None, **kwargs):
	""" AX = RENDER_TABLE(DATA; *args, **kwargs)

		Plots a Pandas DataFrame in a Matplotlib figure using the table annotations.
	"""

	# Resizes the table to fill the entire space and remove the figure axis (if None)
	if ax is None:
		size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
		fig, ax = plt.subplots(figsize=size)
		ax.axis('off')

	# Annotates the table inside the plot
	mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=list(map(lambda x : x.capitalize(), data.columns)), **kwargs)

	# Customize fonts
	mpl_table.auto_set_font_size(False)
	mpl_table.set_fontsize(font_size)

	# Customize the cells face and edge colors
	for k, cell in  six.iteritems(mpl_table._cells):
		cell.set_edgecolor(edge_color)
		if k[0] == 0 or k[1] < header_columns:
			cell.set_text_props(weight='bold', color='w')
			cell.set_facecolor(header_color)
		else:
			cell.set_facecolor(row_colors[k[0]%len(row_colors) ])

	return ax
# --

# ===================

# ==== Commands =====
# Command: /start
def start(update, context):
	""" START(UPDATE,CONTEXT)

		Simply outputs the message of our savior.
	"""

	# Sends the message to the chat
	context.bot.send_message(chat_id=update.effective_chat.id, text="CARAMURU 2000 A LENDA")
# --

# Command: /foto
def foto(update, context):
	""" FOTO(UPDATE,CONTEXT)

		Sends a random picture of a dog from the '/res/dogs/' folder.
	"""

	# Retrives all the image file names and sample a random index
	allFiles = getFiles("res/dogs/")
	idx = np.random.randint(0, len(allFiles))

	# Sends the image to the chat
	context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open("res/dogs/"+allFiles[idx], 'rb'))
# --

# For any unrecognized command
def unknown(update, context):
	""" UNKNOWN(UPDATE,CONTEXT)

		Default message when a unrecognized command is send to the Bot.
	"""

	# Sends the message to the chat
	context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown command :(")
# --

# Command: /compra [args]
@restricted
def compra(update, context):
	""" COMPRA(UPDATE,CONTEXT)

		Registers a purchase in a COMPRAS data file. The command must be used in the form
			/compra [name] [price] [category]
		where [name] is a short description of the purchase (no spaces), [price] is the cost of
		the purchase/service, and [category] is a label to group several different purchases.
	"""

	# Retrives the arguments
	args = context.args

	# %%% Checks if command arguments are okay %%%
	try:
		assert(len(args) == 3)
		float(args[1])

	except:
		# Creates the response message
		response_message = ("Something went wrong :(\n"+
							"Please, see if you are using the command correctly:\n"+
							"\t `/compra [name] [price] [category]`").format(*args)

		# Sends the response message
		context.bot.send_message(chat_id=update.effective_chat.id,
									text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)
		return
	# %%%%%%%%%%%%%%%%%%%%%%

	# Formats some of the arguments to have a standard form on the data
	args[1] = "{0:.2f}".format(float(args[1]))
	args[2] = args[2].capitalize()

	# Creates the dataframe for this new purchase
	add_purchase(*args)

	# Creates the response message
	response_message = ("Thank you!\n"+
						"The purchase *{0}* with value *R$ {1}* was stored within the *{2}* category.\n\n"+
						"Enter /list_compras to see all shoppings on this month.").format(*args)

	# Sends the message to the chat
	context.bot.send_message(chat_id=update.effective_chat.id,
								text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)
# --

# Command: /list_compras
@restricted
def list_compras(update, context):
	""" LIST_COMPRAS(UPDATE,CONTEXT)

		Lists all the purchases done within the current month. This function will retrieve the
		dataframe from the appropriate COMPRAS data file and generate an image visualizing the
		entire table. Also the total expenses of the month are given.
	"""

	# Auxiliary variables
	today    = datetime.today().strftime("%d/%m/%Y")
	filename = "data/compras_"+datetime.today().strftime("%Y-%m")+".csv"

	# List the purchases and prints the total expenses
	try:	# If the file exists
		# Loads the dataframe and calculates the category-based expenses
		compras_df = pd.read_csv(filename)
		costs_df = compras_df.groupby(["type"]).sum().reset_index()

		# Rendes and save the dataframe visualization
		render_table(compras_df)
		plt.savefig('tmp/compras.png', transparent=True, bbox_inches='tight')

		# Creates the response messages
		response_message1 = ("*These are your shoppings until today ("+today+")*\n\n")
		response_message2 = ("*= Total Expenses =*\n" +
							 "\n".join(["*{0}*: R${1:.2f}".format(r['type'], r['cost']) for i,r in costs_df.iterrows()]) +
							 "\n\n*Total*: R$ {0:.2f}".format(costs_df.cost.sum()))

		# Sends the message to the chat
		context.bot.send_message(chat_id=update.effective_chat.id,
									text=markdownfy(response_message1), parse_mode=telegram.ParseMode.MARKDOWN_V2)

		context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open("tmp/compras.png", 'rb'))

		context.bot.send_message(chat_id=update.effective_chat.id,
									text=markdownfy(response_message2), parse_mode=telegram.ParseMode.MARKDOWN_V2)

	except FileNotFoundError: # If the file does not exist
		# Sends the message to the chat
		context.bot.send_message(chat_id=update.effective_chat.id, text="There are still no shoppings on this month :3")

# --

# Command: /agua [args]
@restricted
def agua(update, context):
	""" AGUA(UPDATE,CONTEXT)

		Consults the current AGUA status (1 - There is water, 0 - There is no water) in the house.
		The function can also be used to change this status in the following way:
			/agua [0|no|nao]  ~> Changes the current status to 0 (No water), eventually triggering a daily job
								 that reminds the chat that one should order more water.
			/agua [1|yes|sim] ~> Changes the current status to 1 (there is water), disabling the daily reminder,
								 and also registers a purchase of Água with the proper cost.

		(as of 11/08/2020: drinking water at my house costs R$4.50)
	"""

	# Retrives the arguments
	args = context.args

	# Checks how to respond to the command
	# ===== `/agua` =====
	if(len(args) == 0):
		try:    # If the file exists, opens and checks for the current status
			with open("data/agua_status", "r") as f:
				status = int(f.read())

		except FileNotFoundError:   # If the file does not exist, just outputs a default 1 (there is water)
			status = 1

		# Creates the appropriate response message
		if(status):
			response_message = "There is still water at home :3"
		else:
			response_message = "There is *NO* water at home :("

		# Sends the message to the chat
		context.bot.send_message(chat_id=update.effective_chat.id,
									text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)

	# ===== `/agua [no/yes]` =====
	elif(len(args) == 1):
		if(args[0].lower() in ["no", "nao", "não", "0", "nope"]):
			# Opens the status file and writes the new status
			with open("data/agua_status", "w") as f:
				f.write('0')

			# Sends the confirmation message to the chat
			context.bot.send_message(chat_id=update.effective_chat.id, text="Okay.\nI'll set a daily reminder for you :)")

		elif(args[0].lower() in ["yes", "sim", "1", "yep"]):
			# Opens the status file and writes the new status
			with open("data/agua_status", "w") as f:
				f.write('1')

			# Adds a new purchase of water to the data file
			add_purchase("Água", "4.50", "Food")

			# Creates the response message
			response_message = "Okay!\nI stopped the daily reminders and registered a purchase with value *R$ 4.50* inside the *Food* category."

			# Sends the confirmation message to the chat
			context.bot.send_message(chat_id=update.effective_chat.id,
										text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)

# --

# Command: /falta [args]
@restricted
def falta(update, context):
	""" FALTA(UPDATE,CONTEXT)

		Consults the currently missing itens in the house.
		The function can also be used to add new missing itens in the following way:
			/falta [ITEM] ~> Adds one item with name [ITEM] to the list.
							 Repeated names are not considered.
			/falta [ITEM1] [ITEM2] ... [ITEMN]  ~> Adds several itens at the same time.
	"""

	# Retrives the arguments
	args = context.args

	# ===== `/falta` =====
	if(len(args) == 0):
		try:
			# Opens the file containing the list (the last element is a blank space, and thus is removed)
			with open("data/falta_itens", "r") as f:
				itens = f.read().split('\n')[:-1]

			# Creates the response message
			response_message = ("*These are the itens missing in the house:*\n" +
								"\n".join(["- "+it for it in itens]))

			# Sends the list of itens to the chat
			context.bot.send_message(chat_id=update.effective_chat.id,
										text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)

		except FileNotFoundError:
			# Sends a message to the chat
			context.bot.send_message(chat_id=update.effective_chat.id, text="There is nothing missing in the house :3")

	# ===== `/falta [ITEM1] ... [ITEMN]` =====
	elif(len(args) > 0):
		# Appends the new itens to the file contataining the lists
		with open("data/falta_itens", "a") as f:
			f.write("\n".join(args))
			f.write("\n")

		# Creates the confirmation message accordingly
		if(len(args) == 1):
			response_message = "Okay.\nI added *{0}* to the list of missing itens :)".format(args[0])
		else:
			response_message = "Okay.\nI added these itens to the list of missing itens :)"

		# Sends the message to the chat
		context.bot.send_message(chat_id=update.effective_chat.id,
									text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)

# --

# Command: /falta_remove
@restricted
def falta_remove(update, context):
	""" FALTA_REMOVE(UPDATE,CONTEXT)

		Remove itens from the missing itens list. This is complementary to the `/falta` command.
		The function can also be used in the following ways:
			/falta_remove [ITEM] ~> Removes the item with name [ITEM] from the list.
			/falta_remove [ITEM1] ... [ITEMN]  ~> Removes several itens at the same time.
			/falta_remove ALL ~> Clears the missing itens list.
	"""

	# Retrives the arguments
	args = context.args

	try:
		# ===== `/falta_remove ALL` =====
		if(args[0] == "ALL"):
			# Creates a new empty file
			with open("data/falta_itens", "w") as f:
				f.write("")

			# Sends the message to the chat
			context.bot.send_message(chat_id=update.effective_chat.id, text="Okay!\nI cleared the list of missing itens :)")

		# ===== `/falta_remove [ITEM] ... [ITEMN]` =====
		else:
			# Retrieves the list of itens from the file
			with open("data/falta_itens", "r+") as f:
				itens = f.read().split('\n')[:-1]

			# Searches and removes an individual item, or create a new list without the
			#  itens in the argument
			if(len(args) == 1):
				itens.remove(args[0])
			else:
				itens = [e for e in itens if e not in args]

			# Saves the updated list to the file
			with open("data/falta_itens", "w") as f:
				f.write("\n".join(itens))
				f.write("\n")

			# Creates the confirmation message accordingly
			if(len(args) == 1):
				response_message = "Okay.\nI removed *{0}* from the list of missing itens :)".format(args[0])
			else:
				response_message = "Okay.\nI removed these itens from the list of missing itens :)"

			# Sends the message to the chat
			context.bot.send_message(chat_id=update.effective_chat.id,
										text=markdownfy(response_message), parse_mode=telegram.ParseMode.MARKDOWN_V2)

	except ValueError:  # In case the argument is not on the list
		# Sends the message to the chat
		context.bot.send_message(chat_id=update.effective_chat.id, text=markdownfy("Sorry, the item *{0}* is not on the list :T".format(args[0])),
									parse_mode=telegram.ParseMode.MARKDOWN_V2)

	except FileNotFoundError:   # In case the file has not been created yet
		# Sends the message to the chat
		context.bot.send_message(chat_id=update.effective_chat.id, text="There is nothing missing in the house :3")
# --
# ===================
