Venkata (Sai) Chintalapati (VHC2109)
Brendan Gubbins (BG2751)

----------------------------------------------------------
Our application is essentially a clone for levels.fyi, a salary sharing website for roles in technology. A user can log into the website, create an anonymous post that specifies a job offer they received, including information such as: company name, salary, level (i.e. L3 @ Google), specialization, and years of experience. Admin users then manually approve or reject posts they deem legitimate. Users can view recent posts, search for companies, and filter by level, specialization, location, salary, and years of experience. The application will offer basic visualization of these posts, breaking down top companies by salary in each level. 
One interesting thing about this application is the ability to mix and match when viewing different roles in tech; there are a wide variety of job titles in tech (not limited to SWE), but also levels such as “L3”, specializations like “front-end” and more. Being able to execute interesting queries and visualizing them is really the main intent of the app. One challenge in particular could be distributing a “level system” across companies. Each company has a unique way of identifying their employees ranking (Facebook using E3-E8 for SWE, and IC3-7 for Data Scientists), which could be tricky to implement. Due to the large variance in leveling systems, we opted for a standardized system, 
The entity sets we plan on using are: Users, Companies, Posts, Levels, Specialization, Benefits. Users can be either a regular user or an admin (or both). Posts can either refer to a full-time offer or an internship offer. The relationship sets are straightforward: Users make posts and comment on posts. Posts refer to companies, and are categorized by the engineer’s level and specialization. Benefits are standard across the site and companies can offer said benefits. We will populate our website with data from kaggle as well as generate dummy data (i.e. will probably create 5-10 different benefits and assign them to companies randomly). 



----------------------------------------------------------

Install pip if needed

        sudo apt-get install python-pip

Install libraries

        pip install click flask sqlalchemy


Edit `server.py` to set your database URI

        DATABASEURI = "<your database uri>"


Run it in the shell


        python server.py

Get help:

        python server.py --help

      
