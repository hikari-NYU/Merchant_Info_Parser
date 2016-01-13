from bs4 import BeautifulSoup
import urllib2
import re

class Parser:
	#in class stores container info
	#e.g. <div class="content"> <a class="url" href="https://www.groupon.com/deals/disiac-lounge-2"> -- <a class="merchant-website"> => "div@class:content|a@class:url>href#a@class:merchant-website"
	#initialize
	#@Input: info:str:container info
	def __init__(self, info):
		if info==None:
			#model not exists, capture most common a tags
			self.queries={"name":'a'}
			self.target='href'
			self.merchant_rule=None
			return None
		#initialize attribute list
		self.queries=[]
		#find merchant sign
		merchant_split=info.split('#')
		self.merchant_rule=merchant_split[1]
		target_source=merchant_split[0]
		#find target
		target_split=target_source.split('>')
		target=target_split[1]
		layers=target_split[0]
		#divide layers
		layers=layers.split('|')
		for layer in layers:
			name_divide=layer.split('@')
			name=name_divide[0]
			attr=name_divide[1]
			attr_divide=attr.split(':')
			attr_name=attr_divide[0]
			attr_val=attr_divide[1]
			#format e.g. '"div",{class:"content"}'
			query={"name":name,"attr":{attr_name:attr_val}}
			self.queries.append(query)
		self.target=target

	#accepts url, outputs all matching targets
	#@Input: url:str:url of source page
	#@Output: res:list(str):expected texts/attributes
	def matcher(self, url):
		try:
			#reads HTML codes
			HTML=urllib2.urlopen(url).read()
			#initialize bs4 element
			soup=BeautifulSoup(HTML,'html.parser')
			pool=[soup]
			if self.merchant_rule==None:
				#general situation
				a_tags=soup.find_all(self.queries['name'])
				#count for the most common parent nodes
				a_parents=[(val.parent.name,val.parent.attrs) for val in a_tags]
				max_appear=0
				max_attr=''
				for a in a_parents:
					appear=a_parents.count(a)
					if appear>max_appear:
						max_attr=a
						max_appear=appear
				a_attrs=soup.find_all(max_attr[0],max_attr[1])
				pool=[]
				for a in a_attrs:
					#count for most common tags
					max_appear=0
					max_attr=''
					a_nodes=a.find_all(self.queries['name'])
					a_hrefs=[]
					for a_s in a_nodes:
						try:
							a_hrefs.append(a_s['href'])
							del a_s['href']
							del a_s['rel']
						except:
							a_hrefs.append('')
							pass
					a_nodes_attrs=[val.attrs for val in a_nodes]
					for a_s in a_nodes_attrs:
						appear=a_nodes_attrs.count(a_s)
						if appear>max_appear:
							max_appear=appear
							max_attr=a_s
					#re-append href
					for i in range(len(a_nodes)):
						a_nodes[i]['href']=a_hrefs[i]
					pool.extend(a.find_all(self.queries['name'],max_attr))
			else:
				#degrade to the most specific tag
				for rule in self.queries:
					pool_tmp=[]
					for entity in pool:
						entity_tmp=entity.find_all(rule['name'],rule['attr'])
						pool_tmp.extend(entity_tmp)
					pool=pool_tmp
			#apply final target filter
			res=[]
			for item in pool:
				try:
					#if has href value
					res.append(item[self.target])
				except:
					#if no href value
					pass
		except:
			#invalid url
			res=[]
			pass
		return res

	#accepts deal url, finds company url
	#@Input: url:str:url of deal site
	#@Output: url_merchant:str:url of merchant
	def merchant_finder(self, url):
		if len(url)<1:
			return None
		#gets HTML codes
		try:
			page=urllib2.urlopen(url)
		except:
			return ''
		HTML=page.read()
		#initialize bs4 element
		soup=BeautifulSoup(HTML,'html.parser')
		#close urllib2 link
		page.close()
		if self.merchant_rule==None:
			#undefined site
			#find tag whose text is most similar to website name
			merchant_name=url.split('/')[-1]
			a_links=soup.find_all('a')
			max_sim=0.0
			max_a=None
			for a in a_links:
				text=a.get_text()
				#tag similarity
				exclusive_a=[val for val in merchant_name if val not in text]
				exclusive_b=[val for val in text if val not in merchant_name]
				sim=float(len(exclusive_a)+len(exclusive_b))/(len(merchant_name)+len(text))
				if sim>max_sim:
					max_a=a
					max_sim=sim
			print max_sim
			merchant_url=[max_a['href']]
		else:
			#merchant-tag: a@class:merchant-website
			#split to elements
			tag_split=self.merchant_rule.split('@')
			tag_name=tag_split[0]
			tag_attr=tag_split[1]
			tag_attr_split=tag_attr.split(':')
			tag_attr_name=tag_attr_split[0]
			tag_attr_val=tag_attr_split[1]
			merchant_url=soup.find_all(tag_name,{tag_attr_name:tag_attr_val})
			for i in range(len(merchant_url)):
				merchant_url[i]=merchant_url[i]['href']
		return merchant_url[0]

	#accepts merchant url, finds out phone number and/or email by regular expression match
	#@Input: url:str:url of the merchant; pattern_phone:str:phone pattern; pattern_email:str:email pattern; flag:boolean:whether it is the first layer
	#@Output: (email:list(str),phone:list(str))
	def merchant_info(self, url, pattern_phone, pattern_email,flag):
		#programs to match phone numbers and emails
		prog_phone=re.compile(pattern_phone)
		prog_email=re.compile(pattern_email)
		prog=re.compile(pattern_phone+'|'+pattern_email)
		#initialize for unparsable pages
		phone=[]
		email=[]
		try:
			#gets HTML codes
			page=urllib2.urlopen(url)
			HTML=page.read()
			#initialize bs4 element
			soup=BeautifulSoup(HTML,'html.parser')
			#close connection
			page.close()
			#get rid of format codes
			[script.extract() for script in soup.findAll('script')]
			[style.extract() for style in soup.findAll('style')]
			soup=BeautifulSoup(soup.get_text())
			#from all text find valid strings extract contents that the re compiler accepts
			match_tmp=soup.find_all(string=prog)
			for i in range(len(match_tmp)):
				ph_tmp=prog_phone.search(match_tmp[i])
				if ph_tmp!=None:
					phone.append(ph_tmp.group(0))
				em_tmp=prog_email.search(match_tmp[i])
				if em_tmp!=None:
					email.append(em_tmp.group(0))
			#if not found anything in the index page, dig one layer deeper if it is the original
			if email==[] and phone==[] and flag==0:
				flag=1
				#collect urls
				urls=[]
				links=soup.find_all('a')
				for link in links:
					a_text=link.get_text()
					#matches specific pages only
					if 'contact' in a_text or 'service' in a_text:
						#gets link
						urls.append(link['href'][0])
				for url in urls:
					(phone_tmp,email_tmp)=self.merchant_info(url,pattern_phone,pattern_email,flag)
					phone.extend(phone_tmp)
					email.extend(email_tmp)
			#returns with valid value
			return (phone,email)
		except:
			#unable to parse webpage, return none's
			return ([],[])