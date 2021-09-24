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


DATA_FOLDER = 'consolidated_data/'
DATA_FOLDER_NN = 'consolidated_data_nn/'
TRACKING_TICKERS = 'tracking_tickers'
VOLUME_TRACKER = '0_Tracking_Volume.csv'
VALUE_TRACKER = '0_Tracking_Value.csv'

import json
from datetime import datetime
from shutil import copyfile
import requests
import os
from dataclasses import dataclass
import operator
import matplotlib.pyplot as plt

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

def plotbarchart(tickers, ticker_att, chart_title):
	left = []
	height = []
	tick_label = []
	count = 1
	#chart_title = 'default'
	for tk in tickers:
		left.append(count)
		if (ticker_att == 'volume'):
			height.append(tk.NetVolume)
			#chart_title = 'Net Buy Volume'
		else:
			height.append(tk.NetValue)
			#chart_title = 'Net Buy Value'
		tick_label.append(tk.name)
		count = count +1
	 
	# plotting a bar chart
	plt.bar(left, height, tick_label = tick_label,
	        width = 0.5, color = ['red', 'green'])
	 
	# naming the x-axis
	plt.xlabel('')
	plt.xticks(rotation = 90) # Rotates X-Axis Ticks by 45-degrees
	# naming the y-axis
	plt.ylabel('million Đ')
	# plot title
	plt.title(chart_title)

	# function to show the plot
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

def processdailydata(inputdata, outputfile, NN = False):
	f = open(inputdata)
	d = json.load(f)
	input_data = d["items"][0]

	#process today data
	data = input_data['today']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_today.csv'
	if (NN==False):
		consolidatedata(data,file)
	else:
		consolidatedataNN(data,file)
	# 5 day data
	data = input_data['oneWeek']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_oneweek.csv'
	if (NN==False):
		consolidatedata(data,file)
	else:
		consolidatedataNN(data,file)
  # 5 day data
	data = input_data['oneMonth']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_onemonth.csv'
	if (NN==False):
		consolidatedata(data,file)
	else:
		consolidatedataNN(data,file)
	# year to date data
	data = input_data['yearToDate']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_yearToDate.csv'
	if (NN==False):
		buy_tickers = consolidatedata(data,file)
	else:
		buy_tickers = consolidatedataNN(data,file)

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

	#CWrite tracker data
	tracker_file = outputfile + VALUE_TRACKER
	plot_tk = writetrackingdata(tracker_file,buy_tickers,track_tic,'value', header)

	tracker_file = outputfile + VOLUME_TRACKER
	writetrackingdata(tracker_file,buy_tickers,track_tic,'volume', header)

	#back up daily data
	file = outputfile + datetime.now().strftime("%Y%m%d") + '.json'
	copyfile(inputdata,file)
	print('Backup data: ' + file + '\n')	

	#plot bar chart
	sorted_tks = sorted(plot_tk, key=operator.attrgetter('NetValue'), reverse=True) 
	plotbarchart(sorted_tks,'value', outputfile + 'VALUE')

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

#####EXECUTION####

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
with open('input_data.json','w') as f:
	f.write(dat)

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
with open('input_data_NN.json','w') as f:
	f.write(dat)

##CONSOLIDATE DATA
processdailydata('input_data.json',DATA_FOLDER, False)
processdailydata('input_data_NN.json',DATA_FOLDER_NN, True)

