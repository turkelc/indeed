from __future__ import division # needed for division
import requests # request accesing pages
from bs4 import BeautifulSoup # to scrape html code from pages
import re # to cleanup some data points - searches count-

import pandas as pd # to create a data frame
import numpy as np # generate random times for pauses between requests
import time # package for pausing code
from time import gmtime, strftime

#importing searches & keywords

searches = pd.read_csv('searches.csv')
keywords = pd.read_csv('keywords.csv')

# Defining a function to transform the desired keywords from a dataframe into a dictionary
def dataframeToDict(df):
    ncol = df.columns
    skilldict = {}
    for c in ncol:
        cvalues = df[c].values
        skilldict[c] = cvalues[~pd.isnull(cvalues)]
    return skilldict

keywords = dataframeToDict(keywords)
seperator = "_"

start_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
start = time.time()

p1_start = time.time()

# Creating the Data Frame that will hold the scraped data
df_final = pd.DataFrame(columns=["Search", "Title", "Location", "Company", "Salary", "Summary", "Post_Date", "Link"])
print("We are going to scrape jobs for " + str(searches.shape[0]) + " searches:")
print(" ")
failed = 0
for search in range(0, searches.shape[0], 1):
    df = pd.DataFrame(columns=["Search", "Title", "Location", "Company", "Salary", "Summary", "Post_Date", "Link"])
    url = 'https://il.indeed.com/jobs?q="' + searches.job_title[search].lower().replace(' ', '+') + \
          '"&l=' + searches.job_location[search].lower().replace(' ', '+') + '&' + 'radius=' + str(
        searches.search_radius[search]) + '&jt=' + searches.job_type[search] + \
          '&filter=0&limit=50'
    # making sure job title does not have " "
    #searches.job_title[search] = searches.job_title[search].replace('"', '')

    # request and scrape first page results
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser', from_encoding="utf-8")

    # scraping the total number of jobs for this search
    try:
        results_count = soup.select('#searchCount')
        # cleaning up the scraped string
        results_count = re.sub('\D', '', str(results_count))[1::]
        results_count = int(results_count)
    except:
        results_count = 'NO'
        failed = failed + 1

    print
    "-------------------------"
    print
    ""
    if results_count > 1000 and results_count != "NO":
        print
        "There are " + str(results_count) + " jobs for your [  " + str(search + 1) + " / " + str(
            str(searches.shape[0])) + "  ] search!, but we can only scrape 1000."
    else:
        print
        "There are " + str(results_count) + " jobs for your [  " + str(search + 1) + " / " + str(
            str(searches.shape[0])) + "  ] search!"

    print
    ""
    print
    "link of this search: " + url
    print
    ""

    # to make sure we only scrape the exact number of job posts, otherwise we will have many duplicates

    if results_count < 1000:
        target = results_count
    else:
        target = 1000

    # Loop to request different results pages
    if results_count != 'NO':

        for page in range(0, target, 50):
            if page is not 0:
                progress = int(page / target * 100)
                print
                "Scraped " + str(page) + " jobs [ " + str(progress) + "% ]  [  " + str(search + 1) + " / " + str(
                    str(searches.shape[0])) + "  ]"

            else:

                print
                "Initializing Scraping " + str(target) + " " + str(searches.job_title[search]) + " jobs in " + \
                searches.job_location[search] + "!" + \
                "  [  " + str(search + 1) + " / " + str(str(searches.shape[0])) + "  ]"
                print
                " "
            new_url = url + "&start=" + str(page)
            html = requests.get(new_url)
            soup = BeautifulSoup(html.content, 'html.parser', from_encoding="utf-8")

            # Loop to scrape job title, location, company, salary, synopsis, post date, link

            for each in soup.find_all(class_="result"):
                sponsor = each.find(class_='sponsoredGray')

                if sponsor is None:  # ignore any post that is not organic (sponsored)

                    try:
                        date = each.find('span', {'class': 'date'}).text.replace('\n', '')
                    except:
                        date = 'None'
                    try:
                        joblink = each.find(class_='turnstileLink').get('href')
                        link = 'https://il.indeed.com' + joblink
                    except:
                        link = 'None'
                    try:
                        title = each.find(class_='jobtitle').text.replace('\n', '')
                    except:
                        title = 'None'
                    try:
                        location = each.find('span', {'class': 'location'}).text.replace('\n', '')
                    except:
                        location = 'None'
                    try:
                        company = each.find(class_='company').text.replace('\n', '')
                    except:
                        company = 'None'
                    try:
                        salary = each.find('span', {'class': 'no-wrap'}).text.replace('\n', '')
                    except:
                        salary = 'None'
                    try:
                        summary = each.find('span', {'class': 'summary'}).text.replace('\n', '')
                    except:
                        summary = 'None'
                    # Append the scraped datapoints into a record in the Data Frame

                    df = df.append({'Title': title, 'Location': location, 'Company': company,
                                    'Salary': salary, 'Summary': summary, 'Post_Date': date, 'Link': link,
                                    'Search': searches.job_title[search]}, ignore_index=True)

            # Pausing the loop for a random value in a normal distribution with a mean of 1 seconds, imitate human browsing

            pausetime = int(np.abs(np.random.randn(1) + 1))
            if page != 0:
                print
                "Pausing for " + str(pausetime) + " seconds"
            print
            "-------------------------"
            time.sleep(pausetime)
    else:
        print
        "Skipping  [  " + str(search + 1) + " / " + str(str(searches.shape[0])) + "  ] search!"
    df_final = pd.concat([df_final, df])
    progress = int(df.shape[0] / target * 100)

    if results_count != "NO":
        print
        " "
        print
        "Finished Scraping " + str(df.shape[0]) + " jobs [ " + str(progress) + "% ]  [  " + str(
            search + 1) + " / " + str(searches.shape[0]) + "  ]  [  Total: " + str(df_final.shape[0]) + " jobs  ]"
        print
        " "

        if df.shape[0] != target:
            print
            "Dont worry if the % or number of jobs dont match, Indeed changes the search results on the go as you browse!"

    print
    " "
print
" "
print
" "
print
"-------------------------"
print
"Done with the first phase"
scraped = df_final.shape[0]
if failed != 0:
    print
    "There were " + str(failed) + " searches that had no results, so we only scraped jobs for " + str(
        searches.shape[0] - failed) + " out of the " + str(searches.shape[0]) + " searches."
print
"Total jobs scraped: " + str(scraped) + " jobs."

#df_final.drop_duplicates(keep='first', subset="Link", inplace=True)

#duplicates = scraped - df_final.shape[0]

#print
#"There were " + str(duplicates) + " duplicated jobs that we removed."
#print
#"So we only saved " + str(df_final.shape[0]) + " jobs."
df_final.reset_index(drop=True, inplace=True)
df1 = df_final

p1_duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - p1_start))
print
"Duration: " + p1_duration


#Phase 2: Scraping the body of Job Posts
df_final = df1

p2_start = time.time()

# Loop to request job links collected from the previous phase
target_body = df_final.shape[0]
df_body = pd.DataFrame(columns=["Body"])

for job_link in range(0, target_body, 1):
    job_url = df_final.Link.iloc[job_link]

    if job_link is not 0:
        job_progress =  int(job_link/target_body * 100)
        print("Scraped the Body of " + str(job_link) + " jobs [ " + str(job_progress) + "% ]  [ " + str(job_link) + " / " +  str(target_body) + " ]")

    else:
        print("Initializing Scraping the Body of " + str(target_body) + " jobs!")
        print (" ")
    html = requests.get(job_url)
    soup = BeautifulSoup(html.content, 'html.parser', from_encoding="utf-8")

    # Scrape the body of job link

#    try:
    body = soup.select('div.jobsearch-JobComponent')
    idx = body[0].getText().find('saveJobInlineCallout')
    body = body[0].getText()[0:idx]
#    except:

#        body = "None"

    # Append the scraped body in a Data Frame

    df_body = df_body.append({'Body': body}, ignore_index=True)

    # Pausing the loop for a random value in a normal distribution with a mean of 1 seconds, imitate human browsing

    pausetime = int(np.abs(np.random.randn(1) + 0))
    if job_link != 0:
        print("Pausing for " + str(pausetime) + " seconds")

        print("-------------------------")
        time.sleep(pausetime)

progress =  int((job_link+1)/target_body * 100)

print(" ")
print("Finished Scraping " + str(df_final.shape[0]) + " jobs [ " + str(progress) + "% ]")
print(" ")
print("-------------------------")
print("-------------------------")
print(" ")
print(" ")
# Merging the old and new Data Frames

df_final = pd.merge(df_final, df_body, left_index=True, right_index=True)

scraped = df_final.shape[0]

print("Total jobs scraped: " + str(scraped) + " jobs.")


#df_final.drop_duplicates(keep='first', subset="Body", inplace=True)

#duplicates  = scraped - df_final.shape[0]

#print("We found " + str(duplicates) + " duplicated jobs that we removed.")
#print("So we only saved " + str(df_final.shape[0]) + " jobs.")

df_final.reset_index(drop=True, inplace=True)

p2_duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - p2_start))

df2 = df_final
print("Duration: " + p2_duration)


df_final.to_excel('dataset-deneme.xls')






#Phase 3: Text mining the body of Job Posts
df_final = df2

p3_start = time.time()

print("Initializing extracting keywords from Body of " + str(df_final.shape[0]) + " jobs!")
print(" ")
print("-------------------------")
columns = []
dictionary_count = len(keywords.keys())
# creating columns for keywords
for x in range(0, dictionary_count, 1):

    for y in range(1, len(keywords.get(list(keywords)[x])), 1):
        keyword = keywords.get(list(keywords)[x])[0] + seperator + keywords.get(list(keywords)[x])[y]
        columns.append(keyword)

df_exp = pd.DataFrame(columns=['Experience', 'Exp Min', 'Exp Max'])

df_text = pd.DataFrame(columns=[columns], index=df_final.index)

keyword_count = len(list(df_text.columns.values))

# Experience
for row in range(0, df_final.shape[0], 1):
    try:
        idx = df_final.Body[row].find('years')
        experience = df_final.Body[row][idx - 10:idx + 5]
        exp = re.sub('\D', '', experience)
        experience = df_final.Body[row][idx - 35:idx + 35]
        if len(exp) > 4 or exp == "":
            experience = None
            expmin = None
            expmax = None
        else:
            if len(exp) == 4:
                expmin = exp[0:2]
                expmax = exp[2:4]
            if len(exp) == 3:
                expmin = exp[0]
                expmax = exp[1:3]
            if len(exp) == 2:
                if exp[1] > exp[0]:
                    expmin = exp[0]
                    expmax = exp[1]
                else:
                    expmin = exp
                    expmax = None

            if len(exp) == 1:
                expmin = exp
                expmax = None

            if int(expmin) > 20:
                expmin = None
                expmax = None
                experience = None
            if expmax is not None and (int(expmax) > 20 or int(expmax) <= int(expmin)):
                expmin = None
                expmax = None
                experience = None
    except:
        experience = None
        expmin = None
        expmax = None

    df_exp = df_exp.append({'Experience': experience, 'Exp Min': expmin, 'Exp Max': expmax}, ignore_index=True)

    # Keywords
    cmpny=df_final.Body[row][7]
    for key in range(0, keyword_count, 1):
        word = str(list(df_text.columns.values)[key]).split("_")[1][0:-3]
        idx = df_final.Body[row].find(word)

        if word in df_final.Body.iloc[row] or (len(word) != 2 and word.lower() in df_final.Body.iloc[row]):
            if df_final.Body.iloc[row][idx - 1] is not "H":
                df_text.iloc[row, key] = 1
        else:
            df_text.iloc[row, key] = 0



print(" ")
print(" ")
print("Finished extracting keywords from Body of " + str(df_final.shape[0]) + " jobs [ " + str(progress) + "% ]")

df_final = pd.merge(df_final, df_exp, left_index=True, right_index=True)
df_final = pd.merge(df_final, df_text, left_index=True, right_index=True)

p3_duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - p3_start))

df3 = df_final
print("Duration: " + p3_duration)


#Phase 4: Classifying jobs¶

df_final = df3

p4_start = time.time()

df_title = pd.DataFrame(columns=["General_Title", "Department", "City"])
df_final = df3
for job in range(0, df_final.shape[0], 1):
    point = df_final.Title.iloc[job]
    GT = ''
    pre = ''
    data = ''
    post = 'Analyst'
    dep = 'General'
    if 'Senior ' in point or 'Sr' in point:
        pre = 'Senior '
    # Data
    if 'Data' in point:
        data = 'Data '
        dep = 'Statistics and Data Science'
    # Scientist
    if 'Scientist' in point or 'Science' in point:
        post = 'Scientist'
        dep = 'Statistics and Data Science'
        data = 'Data '
    # Business
    if 'Business' in point or 'BI' in point or 'Intelligence' in point:
        GT = 'Business '
        dep = 'Business'

    # IT
    if 'IT' in point or 'System' in point or 'Security' in point or 'Engineer' in point or \
            'Technical' in point or 'Architect' in point or 'SOX' in point or 'Technology' in point:
        GT = 'IT '
        dep = 'IT'

    # Marketing
    if 'Marketing' in point or 'SEO' in point or 'SEM' in point or 'Campaign' in point or \
            'Product' in point or 'Digital' in point or 'Media' in point or 'Growth' in point or 'Engagement' in point:
        GT = 'Marketing '
        dep = 'Marketing'

    # Supply Chain
    if 'Supply Chain' in point or 'Logistics' in point or 'Operations' in point or 'Procurement' in point:
        GT = 'Supply Chain '
        dep = 'Supply Chain'

    # Finance
    if 'Finance' in point or 'Financial' in point or 'Asset' in point or 'Accounting' in point or \
            'Equity' in point or 'Investment' in point or 'Portfolio' in point or 'Banking' in point or \
            'Credit' in point or 'Risk' in point or 'Venture' in point or 'VC' in point or \
            'Securities' in point or 'Fund' in point or 'Investor' in point or 'Venture' in point or \
            'Capital' in point or 'Revenue' in point or 'Loan' in point or 'Wealth' in point or 'FinTech' in point or \
            'Tax' in point:
        GT = 'Financial '
        dep = 'Finance'
    # Sales
    if 'Sales' in point or 'Operations' in point or 'Account' in point or 'Channel' in point or \
            'Partner' in point or 'Customer' in point or 'Relationship' in point or 'CRM' in point:
        GT = 'Sales '
        dep = 'Sales'
    # HR
    if 'HR' in point or 'Human Resources' in point or 'People' in point or 'Staff' in point or \
            'Organizational' in point or 'OD' in point or 'Talent' in point or 'Compensation' in point or \
            'Rewards' in point or 'Payroll' in point or 'Recruiting' in point or 'Benefit' in point:
        GT = 'HR '
        dep = 'HR'

    # City
    idx = df_final.Location.iloc[job].find(',')
    city = df_final.Location.iloc[job][:idx]


    df_title = df_title.append({'General_Title': (pre + GT + data + post), 'Department': dep, 'City': city},
                               ignore_index=True)

df_final = pd.merge(df_title, df_final, left_index=True, right_index=True)

print
" "
print
" "
print
"Finished filtering " + str(job) + " jobs [ " + str(progress) + "% ]"
print
"-------------------------"

p4_duration = time.strftime("%H:%M:%S", time.gmtime(time.time() - p4_start))

end_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

end = time.time()

total_time = time.strftime("%H:%M:%S", time.gmtime(end - start))

df4 = df_final
print
'We started at ' + start_time
print
'Phase 1 took ' + p1_duration
print
'Phase 2 took ' + p2_duration
print
'Phase 3 took ' + p3_duration
print
'Phase 4 took ' + p4_duration
print
'We finished at ' + end_time
print
'The code ran for ' + total_time

# export dataset
file_date = strftime("%m-%d-%Y", gmtime())
df_final.to_excel('dataset-' + file_date + '.xls')

df_final