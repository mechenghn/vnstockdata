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

DATA_FOLDER = 'consolidated_data/'
TRACKING_TICKERS = 'tracking_tickers'
VOLUME_TRACKER = 'TuDoanh_Tracking_Volume.csv'
VALUE_TRACKER = 'TuDoanh_Tracking_Value.csv'

import json
from datetime import datetime
from shutil import copyfile
import requests
import os
from dataclasses import dataclass
import operator


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

def exploretradeticker(element):
	ticker = element['ticker']
	priceChange=element['priceChange']
	percentPriceChange = element['percentPriceChange']
	totalNetBuyTradeValue = element['totalNetBuyTradeValue']/1e6
	totalNetBuyTradeVolume =element['totalNetBuyTradeVolume']/1e3
	return ticker_info(ticker,priceChange,percentPriceChange,totalNetBuyTradeVolume,totalNetBuyTradeValue)
	#tic_info = ticker_info(ticker,priceChange,percentPriceChange,totalNetBuyTradeVolume,totalNetBuyTradeValue)
	#print(tic_info)
	#word = ticker	+  ',' + str(truncate(priceChange,0)) + ','\
	#	+ str(truncate(percentPriceChange,2)) + ',' \
	#	+ str(truncate(totalNetBuyTradeVolume,0)) + ',' \
	#	+ str(truncate(totalNetBuyTradeValue,0)) 
	#return word

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

def processdailydata(inputdata, outputfile):
	f = open(inputdata)
	d = json.load(f)
	input_data = d["items"][0]

	#process today data
	data = input_data['today']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_today.csv'
	consolidatedata(data,file)
	# 5 day data
	data = input_data['oneWeek']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_oneweek.csv'
	consolidatedata(data,file)
  # 5 day data
	data = input_data['oneMonth']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_onemonth.csv'
	consolidatedata(data,file)
	# year to date data
	data = input_data['yearToDate']	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '_yearToDate.csv'
	buy_tickers = consolidatedata(data,file)

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

	#Check file existence & header existence	
	last_line = ''
	tracker_file = VALUE_TRACKER
	if (os.path.isfile(tracker_file) == False):
		with open(tracker_file,'w') as newf:
			newf.write(header+'\n')
	else:
		with open(tracker_file,'r') as newf:
			lines = newf.readlines()
		last_line = lines[-1]
		#read header
		# TO DO: Replace header here

	with open(VALUE_TRACKER, 'a') as newf:
		towrite = datetime.now().strftime("%Y/%m/%d")
		if (last_line.find(towrite) == -1):
			for ticker in track_tic:
				for tk_info in buy_tickers:
					if (ticker == tk_info.name):
						towrite = towrite +',' + str(truncate(tk_info.NetValue,0))
			newf.write(towrite+'\n')
			print('Write tracking data to ' + VALUE_TRACKER)

	#Write colume tracker data
	last_line = ''
	tracker_file = VOLUME_TRACKER
	if (os.path.isfile(tracker_file) == False):
		with open(tracker_file,'w') as newf:
			newf.write(header+'\n')
	else:
		with open(tracker_file,'r') as newf:
			lines = newf.readlines()
		last_line = lines[-1]
		#read header
		# TO DO: Replace header here

	with open(VOLUME_TRACKER, 'a') as newf:
		towrite = datetime.now().strftime("%Y/%m/%d")
		if (last_line.find(towrite) == -1):
			for ticker in track_tic:
				for tk_info in buy_tickers:
					if (ticker == tk_info.name):
						towrite = towrite +',' + str(truncate(tk_info.NetVolume,0))
			newf.write(towrite + '\n')
			print('Write tracking data to ' + VOLUME_TRACKER)

	#back up daily data
	file = outputfile + datetime.now().strftime("%Y%m%d") + '.json'
	copyfile(inputdata,file)
	print('Backup data: ' + file + '\n')	

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
with open('daily_data.json','w') as f:
	f.write(dat)

##CONSOLIDATE DATA
processdailydata('daily_data.json',DATA_FOLDER)

