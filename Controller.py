from Parser import Parser

#accepts a website name, checks existing models and parse using specific model
#if not exists, use default settings
#@Input: website:str:website name
#@Output: output/website.csv:file:website,phone and email information
def start(website):
	if '/' in website:
		#address
		website_name=website.split('/')[2]
	else:
		website_name=website
	#open file to write
	output=open('output/'+website_name+'.csv','a')
	#define phone and email formats
	#phone in the format of +1XXXXXXXXXX or XXXXXXXXXX or (XXX) XXX-XXXX with optional spaces between digits 3 and 4, and digits 6 and 7
	pattern_phone='([+]1[ ]?\d{3}[ ]?\d{3}[ ]?\d{4})|([+]1[ ]?[(]\d{3}[)][ ]?\d{3}-\d{4})|(\d{3}[ ]?\d{3}[ ]?\d{4})|([(]\d{3}[)][ ]?\d{3}-\d{4})'
	#email with no signs in the first and last digit of username, no signs in domain name and alphabet only in postfix
	pattern_email='([a-zA-Z0-9]([a-zA-Z0-9_.]*[a-zA-Z0-9])*@[a-zA-Z0-9]+.[a-zA-Z]+)'
	parsers=[]
	#get deal urls from model or parameter input
	with open('models','r') as f:
		exists=False
		for line in f:
			#skip comments
			if line.startswith('#'):
				continue
			url_split=line.split(' ')
			name=url_split[0]
			url=url_split[1]
			line=url_split[2]
			#if exists such record
			if website in name:
				ptmp=Parser(line)
				parsers.append((ptmp,url))
				exists=True
		if exists!=True:
			#no such record
			url=website
			line=None
			ptmp=Parser(line)
			parsers.append((ptmp,url))
	#get merchant urls
	for parser in parsers:
		urls=parser[0].matcher(parser[1])
		merchants=[]
		for url in urls:
			merchants.append(parser[0].merchant_finder(url))
		#get merchant emails and phone numbers
		for i in range(len(merchants)):
			url=merchants[i]
			res=parser[0].merchant_info(url,pattern_phone,pattern_email,0)
			#output results if any
			if len(merchants[i])>0:
				#(url,phone,email)
				print(merchants[i],res[0],res[1])
				phone=';'.join(res[0])
				email=';'.join(res[1])
				output.write(merchants[i]+','+phone+','+email+'\n')
	f.close()

def main():
	start('groupon')

if __name__=="__main__":
	main()