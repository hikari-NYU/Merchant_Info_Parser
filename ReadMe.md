####Web Crawler
#####Weicheng Ma
---

######Overview
---

* This system is a focused web crawler designed for parsing merchant information automatically.
* Extraction task is distributed into two levels:
> - Link extraction from seed website
> - Email and phone number extraction from the extracted links

######Technical Details
---

* For each coupon site apply a specific model implying which part of the page to download
* For unknown site find the most common a tags under most common containers
* When parsing emails and phone numbers use patterns to match candidates

######Package Dependencies
---

1. Python urllib2 - HTML parser
2. Python re - Regular Expression operation
3. Python bs4 - HTML analyzer

######Input and Output Specification
---

@Input: model:file:rules for extractable tags of specific websites; website:string:name in model or url to an unfamiliar site
@Output: output/*.csv:file:extracted merchant information in the format(merchant_name,phone,email)

######Usage
---

- 0-0. Install all dependencies
- 0-1. Make sure all files are in one directory and create a directory named 'output'
- 1.1. Modify the file 'models', add name, url and specific attributes for the website you want to parse
- 1.2. Import Controller
- 1.3. Pass the name in the model file or website for an unknown site to the function 'start'
- 1.4. Find the results in the folder 'output' with the parameter you passed as name
- 2.1. Modify the file 'models', add name, url and specific attributes for the website you want to parse
- 2.2. Set the parameter in main function of the file Controller to the name in models or url for an unknown site
- 2.3. In terminal directly call 	python Controller.py
- 2.4. Find the results in the folder 'output' with the parameter to the 'start' function as name

