**This code enables scraping job posts from Indeed Israel.** In order to change the country, change "il" to "www" in urls in rows 40 and 123.
The purpose of the code was to be able to get a Dataset that captures different jobs posts from Indeed that can be analyzed to understand the job market demand, in terms of job titles, skills, industries and locations.

This code is a revised version of [Zeus Habash's repository](https://github.com/zeus-habash/Scraping-jobs-from-Indeed) of code to scrape indeed.com, adapted to Python 3 and to some changes in html elements on Indeed website. Furthermore handled a few errors.

**"The code structure**
* Importing needed packages.

* Loading CSV files that are the inputs for the code, the files contain the job searches and keywords you are looking for in each job.

* Phase 1 - Scraping Job links: This code will create a dataset of all the job searches with links for each job.

* Phase 2 - Scraping the body of job posts: This code will pull the body text of each job in the created dataset.

* Phase 3 - Text mining the body of job posts: This code will look for the desired keywords and min years of experience needed for each job.

* Phase 4 - Classifying jobs: This code classifies the jobs into different categories: Job title, Business Function / Department, and city.

**What to do with the searches and keywords CSV files**

These files act as inputs for the code, to make it easier to edit based on need.

You should edit your searches and desired keywords based on your need before running the python code.

* **A) searches.csv:**
This file contains the desired searches needed to be scraped from Indeed: There are 4 columns:

Job Title: The job title you want to search for.

Job Location: The location you want to search for jobs in.

search radius (in miles): the radius of your job search.

Note: It is better to have a small radius for different nearby cities, because Indeed limits you to 1000 results for each search.
Job Type: You choose the desired job type in this field (fulltime, parttime, contract, commission, internship, temporary, all).
* **B) keywords.csv:**
This file contains the desired keywords that you want to check if they are mentioned in the body text of each job post. The results for each keyword will be shown in a binary format ('1' if the word exists in the job post, '0' if the word does NOT exist in the job post.)

Things to know about keywords.csv:
Each keyword in this file will become a binary variable in the final dataset.

Each column in the CSV file represents a category of keywords (e.g.: Soft Skills, Analytics Skills, Programing Languages.) The header of the dataset has names of each category, so that the user can easily know what the different categories of keywords are.

The second row in the dataset has acronyms for each keyword category, these acronyms will become prefixes for the keywords when they are appended in the final dataset, to keep the keywords' variables nice and clean to find and use.

You can add as many categories as you want, just make sure you follow the same format as the file shared in my repository and read the guidelines.

**Things to know while running the code**
The code might take a long time to execute depending on the amount of job searches needed, however the code will show you the progress made while it is running, so you can sit, relax, or even run the code and go to sleep and come back later to see the results.

The code will track time needed for each phase in the code and will give you a summary at the end of Phase 4. Here is the summary I got after I ran the code for my 1240 job searches:

Phase 1 took 02:00:17
Phase 2 took 02:19:51
Phase 3 took 00:04:45
Phase 4 took 00:00:15
The code ran for 04:25:11
Several job searches will show duplicate job posts, but do not worry the code will filter duplicate jobs twice: First after Phase 1: Removing jobs with the same job link. Second after Phase 2: Removing jobs with the same job body of text."
