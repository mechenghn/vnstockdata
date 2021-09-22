#Thinh viet code. Muc dich nghien cuu Chung khoan VN
#Share voi Linh Tam
#Khong share lai
#Have fun

import json
from datetime import datetime
from shutil import copyfile
import requests
import os

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
	word = ticker	+  ',' + str(truncate(priceChange,0)) + ','\
		+ str(truncate(percentPriceChange,2)) + ',' \
		+ str(truncate(totalNetBuyTradeVolume,0)) + ',' \
		+ str(truncate(totalNetBuyTradeValue,0)) 
	return word

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
		totalNetBuyTradeValue = data['totalNetBuyTradeValue']/1e6
		f.write('TOTAL NET BUY,' + str(truncate(totalNetBuyTradeValue,0)) +'\n') 
		totalNetSellTradeVolume = data['totalNetSellTradeVolume']/1e3
		totalNetSellTradeValue = data['totalNetSellTradeValue']/1e6
		f.write('TOTAL NET SELL,' + str(truncate(totalNetSellTradeValue,0)) +'\n') 
		print('BUY TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		f.write('BUY TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		buy = data['buy']
		for buy_element in buy:
			print(exploretradeticker(buy_element))
			f.write(exploretradeticker(buy_element) +'\n') 

		print('SELL TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		f.write('SELL TICKET, PRICE CHANGE, PERCENT PRICE CHANGE, NET VOL, NET VALUE\n')
		sell = data['sell']
		for sell_element in sell:
			print(exploretradeticker(sell_element))
			f.write(exploretradeticker(sell_element) +'\n') 


def processdailydata(inputdata, outputfile):
	f = open(inputdata)
	d = json.load(f)
	input_data = d["items"][0]
	data_today = input_data['today']
	data_oneweek = input_data['oneWeek']
	data_oneMonth = input_data['oneMonth']
	data_yeartodate = input_data['yearToDate']

	#process today data
	data = data_yeartodate	
	file = outputfile + datetime.now().strftime("%Y%m%d") + '.csv'
	consolidatedata(data,file)

	#back up daily data
	file = outputfile + datetime.now().strftime("%Y%m%d") + '.json'
	copyfile(inputdata,file)

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
processdailydata('daily_data.json','consolidated data/TUDOANH_yearToDate_')

