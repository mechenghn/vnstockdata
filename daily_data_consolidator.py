#Thinh viet code. Muc dich nghien cuu Chung khoan VN
#tested on Python3.9 
#Share voi Linh Tam
#Khong share lai
#Have fun

#Revision
#v1.0
# - Get daily data from SSI
# - Auto backup data to json with date
# - Save yeartoDate data to CSV
#v1.1
# - Sort data before saving 
# - Save Tracking data for a tracking list of stocks
#v1.2
#- plot tracking ticker value/volume
#v1.3
#- auto update tracker header when the tracking list changes
#- collect foreign data
#v1.4 
# -plot historic data of tickers using 'plot' argument
#v1.5
# -plot single ticket buy/sell history 


#Run format
#python3.9 daily_data_consolidater.py -arg1 -arg2
# - arg1 == null >> Collect daily data
# - arg1 == plot >> Plot data
# - arg2: specific ticker to plot historic data

DATA_FOLDER = 'consolidated_data/'
DATA_FOLDER_NN = 'consolidated_data_nn/'
TRACKING_TICKERS = 'tracking_tickers'
VOLUME_TRACKER = '0_Tracking_Volume'
VALUE_TRACKER = '0_Tracking_Value'
NO_OF_PLOTTING_TICKERS = 10

import json
from datetime import datetime
from shutil import copyfile
import requests
import os
import sys
from dataclasses import dataclass
import operator
import matplotlib.pyplot as plt
import csv
import glob

@dataclass
class ticker_info:
    name: str
    priceChange: float = 0.0
    percentPriceChange: float = 0.0
    NetVolume: float = 0.0
    NetValue: float =0.0

def truncate(n, digit):
	pw = pow(10,digit)
	if n is None:
		return 0
	elif (n == 0):
		return 0
	else:	
		return int(n*pw)/pw

def plotbarchart(tickers, ticker_att, chart_title, retaintime = 3):
	left = []
	height = []
	tick_label = []
	count = 1
	ymin = 0.0
	ymax = 1500.0
	#chart_title = 'default'
	for tk in tickers:
		left.append(count)
		if (ticker_att == 'volume'):
			height.append(tk.NetVolume/1e3)
			if (ymin > float(tk.NetVolume/1e3)):
				ymin = float(tk.NetVolume/1e3) * 0.5
		else:
			height.append(tk.NetValue/1e3)
			if (ymin > float(tk.NetValue/1e3)):
				ymin = float(tk.NetValue/1e3) * 0.5
		tick_label.append(tk.name)
		count = count + 1

	# plotting a bar chart
	plt.bar(left, height, tick_label = tick_label,
	        width = 0.5, color = ['red', 'green'])
	
	#indicate number on top of each bar
	for index,data in enumerate(height):
		plt.text(x=index + 0.7, y = data + 3, s=f"{round(data)}" , fontdict=dict(fontsize=10)) 

	# naming the x-axis
	plt.xlabel('')
	plt.xticks(rotation = 60) # Rotates X-Axis Ticks by 45-degrees
	# naming the y-axis
	if (ticker_att == 'volume'):
		plt.ylabel('mln')
	else:
		plt.ylabel('bln VND')
	# plot title
	plt.title(chart_title)

	axes = plt.gca()
	#axes.set_xlim([xmin,xmax])
	#axes.set_ylim([ymin,ymax])

	# function to show the plot
	if (retaintime > 0):
		plt.show(block=False)
		plt.pause(retaintime)
		plt.close()
	else:
		plt.show()


def exploretradeticker(element):
	ticker = element['ticker']
	priceChange=element['priceChange']
	percentPriceChange = element['percentPriceChange']
	totalNetBuyTradeValue = element['totalNetBuyTradeValue']/1e6
	totalNetBuyTradeVolume =element['totalNetBuyTradeVolume']/1e3
	return ticker_info(ticker,priceChange,percentPriceChange,totalNetBuyTradeVolume,totalNetBuyTradeValue)

def exploretradetickerNN(element):
	ticker = element['ticker']
	priceChange=element['priceChange']
	percentPriceChange = element['percentPriceChange']
	totalNetBuyTradeValue = element['foreignNetBuyValue']/1e6
	totalNetBuyTradeVolume =element['foreignNetSellValue']/1e3
	return ticker_info(ticker,priceChange,percentPriceChange,totalNetBuyTradeVolume,totalNetBuyTradeValue)
		

def consolidatedata(data,outputfile):
	with open(outputfile, 'w') as f:
		comGroupCode = data['comGroupCode']
		fromDate = (data['fromDate'].split('T',2))[0]
		toDate = (data['toDate'].split('T',2))[0]
		timeRange=data['timeRange']
		f.write('FROM DATE,' + str(fromDate) +'\n')
		f.write('TO DATE,' + str(toDate) + '\n') 
		totalBuyTradeVolume = data['totalNetBuyTradeVolume']/1e3
		totalBuyTradeValue = data['totalNetBuyTradeValue']/1e6
		totalSellTradeVolume = data['totalNetSellTradeVolume']/1e3
		totalSellTradeValue = data['totalSellTradeValue']/1e6
		totalNetBuyTradeVolume = data['totalNetBuyTradeVolume']/1e3
		totalNetBuyTradeValue = data['totalNetBuyTradeValue']/1e9
		f.write('TOTAL NET BUY (bln),' + str(truncate(totalNetBuyTradeValue,0)) +'\n') 
		totalNetSellTradeVolume = data['totalNetSellTradeVolume']/1e3
		totalNetSellTradeValue = data['totalNetSellTradeValue']/1e9
		f.write('TOTAL NET SELL (bln),' + str(truncate(totalNetSellTradeValue,0)) +'\n') 
		#print('BUY TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		f.write('\nBUY TICKET, PRICE CHANGE (k), PERCENT PRICE CHANGE, NET VOL (k), NET VALUE (mln)\n')
		buy = data['buy']
		tickers = []
		for buy_element in buy:
			tickers.append(exploretradeticker(buy_element))
		sorted_tickers = sorted(tickers, key=operator.attrgetter('NetValue'), reverse=True) 
		for tk in sorted_tickers:
			tk_info = (tk.name +  ',' + str(truncate(tk.priceChange,0)) + ','\
						+ str(truncate(tk.percentPriceChange,2)) + ',' \
						+ str(truncate(tk.NetVolume,0)) + ',' \
						+ str(truncate(tk.NetValue,0)))
			f.write(tk_info +'\n')			 
		#print('SELL TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		f.write('\nSELL TICKET, PRICE CHANGE (k), PERCENT PRICE CHANGE, NET VOL (k), NET VALUE (mln)\n')
		sell = data['sell']
		ret_tickers = tickers
		tickers = []
		for sell_element in sell:
			tickers.append(exploretradeticker(sell_element))
		sorted_tickers = sorted(tickers, key=operator.attrgetter('NetValue'), reverse=False) 
		for tk in sorted_tickers:
			tk_info = (tk.name +  ',' + str(truncate(tk.priceChange,0)) + ','\
						+ str(truncate(tk.percentPriceChange,2)) + ',' \
						+ str(truncate(tk.NetVolume,0)) + ',' \
						+ str(truncate(tk.NetValue,0)))
			f.write(tk_info +'\n')
		print('Write data: ' + outputfile + '\n')	
		return ret_tickers	

def plottopbuysale(buy_tickers, depth, title, TTL = 0):
	sorted_tks = sorted(buy_tickers, key=operator.attrgetter('NetValue'), reverse=True) 
	plot_tk=[]
	count=0
	if (depth > len(sorted_tks)):
		return
	for tk in sorted_tks:
		if(count < depth and tk.NetValue > 0):
			plot_tk.append(tk)
		if(count > (len(sorted_tks)-depth) and tk.NetValue < 0):
			plot_tk.append(tk)
		count = count + 1
	plotbarchart(plot_tk,'value', title, TTL)

def plottopbuy(buy_tickers, depth, title, TTL = 0):
	sorted_tks = sorted(buy_tickers, key=operator.attrgetter('NetValue'), reverse=True) 
	plot_tk=[]
	count=0
	if (depth > len(sorted_tks)):
		return
	for tk in sorted_tks:
		if(count < depth and tk.NetValue > 0):
			plot_tk.append(tk)
			count = count + 1
		
	plotbarchart(plot_tk,'value', title, TTL)

def plotuptodatedata(inputdata, NN = False):
	f = open(inputdata)
	d = json.load(f)
	input_data = d["items"][0]

	#1 day
	data = input_data['today']	
	file = 'dummy.csv'
	if (NN == False):
		buy_tickers=consolidatedata(data,file)
		plottopbuysale(buy_tickers,10,'Value - TODAY',0)
	else:
		buy_tickers=consolidatedataNN(data,file)
		plottopbuysale(buy_tickers,10,'Value NN - TODAY',0)
	

	#5day
	data = input_data['oneWeek']	
	file = 'dummy.csv'
	if (NN== False):
		buy_tickers=consolidatedata(data,file)
		plottopbuysale(buy_tickers,10,'Value - 5 DAYS',0)
	else:
		buy_tickers=consolidatedataNN(data,file)
		plottopbuysale(buy_tickers,10,'Value NN - 5 DAYS',0)
	

	#20 day data
	data = input_data['oneMonth']	
	file = 'dummy.csv'
	if (NN == False):
		buy_tickers=consolidatedata(data,file)
		plottopbuysale(buy_tickers,20,'Top BUY Value - LAST 20 DAYS',0)
	else:
		buy_tickers=consolidatedataNN(data,file)
		plottopbuysale(buy_tickers,20,'Top BUY Value NN- LAST 20 DAYS',0)
	

	# year to date data
	data = input_data['yearToDate']	
	if (NN == False):
		buy_tickers=consolidatedata(data,file)
		plottopbuy(buy_tickers,20,'Top BUY Value - YEAR TO DATE',0)
	else:
		buy_tickers=consolidatedataNN(data,file)
		plottopbuy(buy_tickers,20,'Top BUY Value NN- YEAR TO DATE',0)
	



def processdailydata(inputdata, outputfile, NN = False):
	f = open(inputdata)
	d = json.load(f)
	input_data = d["items"][0]

	#Read a list of tickers to track
	print('Tracking list: ')
	text_file = open('tracking_tickers', "r")
	bRead = True
	header = "Date"
	track_tic=[]
	while bRead == True:
		line = text_file.readline()
		symbol = line.replace('\n', '')
		if len(symbol) > 1:
			header = header + ',' + symbol
			track_tic.append(symbol)
			print(symbol)
		else:
			bRead = False
			text_file.close()

	#process today data
	data = input_data['today']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_today.csv'
	if (NN==False):
		buy_tickers=consolidatedata(data,file)
		plottopbuysale(buy_tickers,10,'Value - TODAY',0)
	else:
		buy_tickers=consolidatedataNN(data,file)
	
	# 5 day data
	data = input_data['oneWeek']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_oneweek.csv'
	if (NN==False):
		buy_tickers=consolidatedata(data,file)
	else:
		buy_tickers=consolidatedataNN(data,file)
	plottopbuysale(buy_tickers,7,'Value - WEEK',0)

    #20 day data
	data = input_data['oneMonth']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_onemonth.csv'
	if (NN==False):
		buy_tickers=consolidatedata(data,file)
	else:
		buy_tickers=consolidatedataNN(data,file)
	plottopbuysale(buy_tickers,10,'Value - MONTH',0)

	#Write tracker data
	tracker_file = outputfile + VALUE_TRACKER + '_month.csv'
	plot_tk = writetrackingdata(tracker_file,buy_tickers,track_tic,'value', header)

	tracker_file = outputfile + VOLUME_TRACKER + '_month.csv'
	writetrackingdata(tracker_file,buy_tickers,track_tic,'volume', header)
	#plot bar chart
	sorted_tks = sorted(plot_tk, key=operator.attrgetter('NetValue'), reverse=True) 
	plotbarchart(sorted_tks,'value', outputfile + 'VALUE - TRACK LIST - MONTH')

	# year to date data
	data = input_data['yearToDate']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_yearToDate.csv'
	if (NN==False):
		buy_tickers = consolidatedata(data,file)
	else:
		buy_tickers = consolidatedataNN(data,file)

	#Write tracker data
	tracker_file = outputfile + VALUE_TRACKER + '.csv'
	plot_tk = writetrackingdata(tracker_file,buy_tickers,track_tic,'value', header)

	tracker_file = outputfile + VOLUME_TRACKER + '.csv'
	writetrackingdata(tracker_file,buy_tickers,track_tic,'volume', header)

	#back up daily data
	file = outputfile + datetime.now().strftime("%Y%m%d") + '.json'
	copyfile(inputdata,file)
	print('Backup data: ' + file + '\n')	

	#plot bar chart
	sorted_tks = sorted(plot_tk, key=operator.attrgetter('NetValue'), reverse=True) 
	plotbarchart(sorted_tks,'value', outputfile + 'VALUE - yearToDate')


def consolidatedataNN(data,outputfile):
	with open(outputfile, 'w') as f:
		comGroupCode = data['comGroupCode']
		fromDate = (data['fromDate'].split('T',2))[0]
		toDate = (data['toDate'].split('T',2))[0]
		timeRange=data['timeRange']
		f.write('FROM DATE,' + str(fromDate) +'\n')
		f.write('TO DATE,' + str(toDate) + '\n') 
		#totalBuyTradeVolume = data['totalNetBuyTradeVolume']/1e3
		totalBuyTradeValue = data['foreignBuyValue']/1e6
		#totalSellTradeVolume = data['totalNetSellTradeVolume']/1e3
		totalSellTradeValue = data['foreignSellValue']/1e6
		#totalNetBuyTradeVolume = data['totalNetBuyTradeVolume']/1e3
		totalNetBuyTradeValue = data['foreignNetBuyValue']/1e9
		f.write('TOTAL NET BUY (bln),' + str(truncate(totalNetBuyTradeValue,0)) +'\n') 
		#totalNetSellTradeVolume = data['totalNetSellTradeVolume']/1e3
		totalNetSellTradeValue = data['foreignNetSellValue']/1e9
		f.write('TOTAL NET SELL (bln),' + str(truncate(totalNetSellTradeValue,0)) +'\n') 
		#print('BUY TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		f.write('\nBUY TICKET, PRICE CHANGE (k), PERCENT PRICE CHANGE, NET VOL (k), NET VALUE (mln)\n')
		buy = data['buy']
		tickers = []
		for buy_element in buy:
			tickers.append(exploretradetickerNN(buy_element))
		sorted_tickers = sorted(tickers, key=operator.attrgetter('NetValue'), reverse=True) 
		for tk in sorted_tickers:
			tk_info = (tk.name +  ',' + str(truncate(tk.priceChange,0)) + ','\
						+ str(truncate(tk.percentPriceChange,2)) + ',' \
						+ str(truncate(tk.NetVolume,0)) + ',' \
						+ str(truncate(tk.NetValue,0)))
			f.write(tk_info +'\n')			 
		#print('SELL TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		f.write('\nSELL TICKET, PRICE CHANGE (k), PERCENT PRICE CHANGE, NET VOL (k), NET VALUE (mln)\n')
		sell = data['sell']
		ret_tickers = tickers
		tickers = []
		for sell_element in sell:
			tickers.append(exploretradetickerNN(sell_element))
		sorted_tickers = sorted(tickers, key=operator.attrgetter('NetValue'), reverse=False) 
		for tk in sorted_tickers:
			tk_info = (tk.name +  ',' + str(truncate(tk.priceChange,0)) + ','\
						+ str(truncate(tk.percentPriceChange,2)) + ',' \
						+ str(truncate(tk.NetVolume,0)) + ',' \
						+ str(truncate(tk.NetValue,0)))
			f.write(tk_info +'\n')
		print('Write data: ' + outputfile + '\n')	
		return ret_tickers	

def writetrackingdata(tracker_file, tickers,track_tic, datatype = 'value', header = ''):
	last_line = ''
	plot_tk =[]
	old_header = header
	#print('header: ' + header)
	if (os.path.isfile(tracker_file) == False):
		with open(tracker_file,'w') as newf:
			newf.write(header+'\n')
		last_line = header
	else:
		with open(tracker_file,'r') as newf:
			lines = newf.readlines()
		if (len(lines)>0):
			last_line = lines[-1]
			old_header = lines[0].replace("\n",'')
			#print('OLD HEADER: ' + old_header)
			if (old_header!=header):
				print('Relace header')
				with open(tracker_file,'w') as newf:
					lines[0]=header+'\n'
					for line in lines:
						newf.write(line)
		else:
			last_line = ''

	with open(tracker_file, 'a') as newf:
		towrite = datetime.now().strftime("%Y/%m/%d")
		for ticker in track_tic:
				bMatch = False
				for tk_info in tickers:
					if (ticker == tk_info.name):
						if (datatype == 'value'):
							value = tk_info.NetValue
						else:
							value = tk_info.NetVolume
						towrite = towrite +',' + str(truncate(value,0))
						plot_tk.append(tk_info)
						bMatch = True
						#print('DEBUG: match ticker ' +tk_info.name + ' ' + str(truncate(tk_info.NetValue,0)))
				if (bMatch == False):
					towrite = towrite +',0'

		if (last_line.find(towrite) == -1):
			newf.write(towrite+'\n')
			print('Write tracking data to ' + tracker_file)
		return plot_tk

def exploresingleticker(inputdata, ticker, buy_or_sell = True, timeRange = 'm', NN = False):
	f = open(inputdata)
	d = json.load(f)
	input_data = d["items"][0]
	if (timeRange == 'd'):
		data = input_data['today']
	elif (timeRange == 'w'):
		data =input_data['oneWeek']
	elif (timeRange == 'y'):
		data =input_data['yearToDate']
	else:
		data =input_data['oneMonth']

	if (buy_or_sell == True):
		buy = data['buy']
	else:
		buy = data['sell']
	tickers = []
	for buy_element in buy:
		if (NN == False):
			tickers.append(exploretradeticker(buy_element))
		else:
			tickers.append(exploretradetickerNN(buy_element))
	for tk in tickers:
		if (tk.name == ticker):
			return tk.NetValue;
	return 0

def plotsingletickerhistory(single_ticker):
	print('Plot single ticker: ' + single_ticker)
	#tudoanh
	path = os.getcwd() + '/consolidated_data/*.json'
	files = glob.glob(path)
	sorted_by_mtime_ascending = sorted(files, key=lambda t: os.stat(t).st_mtime)
	tickers = []
	count = 0
	for data_path in sorted_by_mtime_ascending:
		tk_date = data_path[data_path.find('.json')-8:data_path.find('.json')]
		if (count == 0):
			tk_val = exploresingleticker(data_path,plot_single_tk,True,'y')
		else:
			tk_val = exploresingleticker(data_path,plot_single_tk,True,'d') 
			cumulative_val = tickers[count-1].NetValue
			tk_val = float(tk_val) + cumulative_val
		count+=1
		tickers.append(ticker_info(tk_date,0,0,0,float(tk_val)))
	plotbarchart(tickers,'value',single_ticker + ' Tu doanh',-1)

	#nn
	path = os.getcwd() + '/consolidated_data_nn/*.json'
	files = glob.glob(path)
	sorted_by_mtime_ascending = sorted(files, key=lambda t: os.stat(t).st_mtime)
	tickers = []
	count = 0
	for data_path in sorted_by_mtime_ascending:
		tk_date = data_path[data_path.find('.json')-8:data_path.find('.json')]
		if (count == 0):
			tk_val = exploresingleticker(data_path,plot_single_tk,True,'y', True)
		else:
			tk_val = exploresingleticker(data_path,plot_single_tk,True,'d', True) 
			cumulative_val = tickers[count-1].NetValue
			tk_val = float(tk_val) + cumulative_val
		count+=1
		tickers.append(ticker_info(tk_date,0,0,0,float(tk_val)))
	plotbarchart(tickers,'value',single_ticker + ' NN',-1)



#####EXECUTION####
arg_count=0
op_mode = 'fetch'
plot_single_tk = 'XXX'
for arg in sys.argv:
	print(arg)
	if (arg_count == 1):
		if (arg == 'plot'):
				op_mode = 'plot'
	if (arg_count == 2):
		if (arg.isnumeric() and int(arg) < 30 and int(arg) > 5):
			NO_OF_PLOTTING_TICKERS = int(arg)
		elif (arg.upper() == 'ALL'):
			plot_single_tk = 'XXX'
		else:
			plot_single_tk = arg.upper()
	if (arg_count == 3):
		plot_single_tk = arg.upper()
	arg_count = arg_count+1
if (op_mode == 'fetch'):
	with open('input_data.json','w') as f:
		dat = os.popen("curl 'https://fiin-market.ssi.com.vn/MoneyFlow/GetProprietaryV2?language=vi&ComGroupCode=VNINDEX&time=1632236211813' \
	  -H 'Connection: keep-alive' \
	  -H 'Pragma: no-cache' \
	  -H 'Cache-Control: no-cache' \
	  -H 'sec-ch-ua: \"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\"' \
	  -H 'sec-ch-ua-mobile: ?0' \
	  -H 'X-Fiin-Key: KEY' \
	  -H 'Content-Type: application/json' \
	  -H 'Accept: application/json' \
	  -H 'X-Fiin-User-ID: ID' \
	  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36' \
	  -H 'X-Fiin-Seed: SEED' \
	  -H 'sec-ch-ua-platform: \"macOS\"' \
	  -H 'Origin: https://iboard.ssi.com.vn' \
	  -H 'Sec-Fetch-Site: same-site' \
	  -H 'Sec-Fetch-Mode: cors' \
	  -H 'Sec-Fetch-Dest: empty' \
	  -H 'Referer: https://iboard.ssi.com.vn/' \
	  -H 'Accept-Language: en-US,en;q=0.9' \
	  --compressed").read()
		f.write(dat)

	with open('input_data_NN.json','w') as f:
		dat = os.popen("curl 'https://fiin-market.ssi.com.vn/MoneyFlow/GetForeign?language=vi&ComGroupCode=VNINDEX&time=1632450311261' \
	  -H 'Connection: keep-alive' \
	  -H 'sec-ch-ua: \"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\"' \
	  -H 'sec-ch-ua-mobile: ?0' \
	  -H 'X-Fiin-Key: KEY' \
	  -H 'Content-Type: application/json' \
	  -H 'Accept: application/json' \
	  -H 'X-Fiin-User-ID: ID' \
	  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36' \
	  -H 'X-Fiin-Seed: SEED' \
	  -H 'sec-ch-ua-platform: \"macOS\"' \
	  -H 'Origin: https://iboard.ssi.com.vn' \
	  -H 'Sec-Fetch-Site: same-site' \
	  -H 'Sec-Fetch-Mode: cors' \
	  -H 'Sec-Fetch-Dest: empty' \
	  -H 'Referer: https://iboard.ssi.com.vn/' \
	  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \
  	--compressed").read()
		f.write(dat)

	#CONSOLIDATE DATA
	processdailydata('input_data.json',DATA_FOLDER, False)
	processdailydata('input_data_NN.json',DATA_FOLDER_NN, True)

##Plot Tracking tickers
if (op_mode=='plot'):
	print('START PLOTTING')

	#looping through the data to find the tickers information
	if (plot_single_tk!='XXX'):
		plotsingletickerhistory(plot_single_tk)
	else:
		plotuptodatedata('input_data.json')
		plotuptodatedata('input_data_NN.json', True)

	#Read tracking data
#	tracker_file = DATA_FOLDER + VALUE_TRACKER + '.csv'
#	data = list(csv.reader(open(tracker_file)))
 
	#Plot year to date data
#	tickers=[]
#	for i in range(min(len(data[0])-1,NO_OF_PLOTTING_TICKERS)):
#		last_row_idx = len(data)-1
#		ticker = ticker_info(data[0][i+1],0,0,0,float(data[last_row_idx][i+1]))
#		tickers.append(ticker)
#		last_date = data[last_row_idx][0]
#	sorted_tickers = sorted(tickers, key=operator.attrgetter('NetValue'), reverse=False) 
#	plotbarchart(sorted_tickers,'value','Value Year To Date ' + last_date)

#	#plot each tiker data
#	if (plot_single_tk == 'XXX'):
#		for i in range(len(data[0])):
#			if (i>0 and i <= len(data[0])):
#				tk_title = str(data[0][i])
#				tickers = []
#				for j in range(len(data)):
#					if (j > 0):
#						tk_date = data[j][0]
#						if (i < len(data[j])):
#							tk_val = data[j][i]
#						else:
#							tk_val = 0.0
#						ticker = ticker_info(tk_date,0,0,0,float(tk_val))
#						tickers.append(ticker)
#				plotbarchart(tickers,'value',tk_title)

	



	