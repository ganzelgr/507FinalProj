# 507FinalProj

#### Data sources used:

This project used data from the website www.twitchmetrics.net. The top 50 english-speaking streamers under the categories most watched, fastest growing, highest peak vierership, most popular, and most followed categories were scraped. From here, the program then crawled to the page belonging to each streamer to pull additional information, such as their monthly performance, date joined, total follower count, and featured snipped (if there was one).

#### Here is a brief overview of the code's structure:
* Code for caching
* Streamer class definition
* Defintion of scrape_twitch_metrics_page function that scrapes top 50 for all categories except most watched 
  * returns a list of usernames in ranked order, and a growing list that contains streamer instances from the union of all categories
* Definition of scrape_viewership_page function that scraped top 50 for most watched category
  * returns a list of usernames in ranked order, and a growing list that contains streamer instances from the union of all categories
* Definition of reset_db() that does all of the scraping, and then recreates and populates the databases with the information
* Definition of display_rankings function that pulls the rankings for a category from the database and prints it out in nicely formatted table in command prompt
* Definition of display_streamer function that pulls information on a user-specified streamer from the database and prints it in a nicely formatted way in command prompt
* Definintion of plot_rankings function that plots the rankings for a user-specified category as a barplot in plotly*
* Definition of plot_pie function that uses a dictionary to get the count of how many streamers are playing each game, and displays that information in a pie chart on plotly*
* The main interactive code
  
#### User guide: 

In order to run the code, download the final_proj.py and requirements.txt files and place them in the same directory. Create a virtual environment and use requirements.txt to load the needed modules to run the python file. Upon running the python file, the user will be prompted for a command. Enter help to see a list of available commands and their functions.
  
#### Here is how to access the four display options:
1. Enter 'rankings [category_name]' to view the rankings for a category displayed in a well formatted table. The possible category names are displayed upon entering 'help'
2. Once you have the rankings for a category displayed, enter 'plot' to have the graph appear in plotly*
3. Enter 'streamer [streamer_name]' to view additional information on any streamer
4. Enter 'distribution' to see a pie chart showing a distribution of the games being played by the top ranked streamers.*

**For help on how to get started using plotly, please visit https://plot.ly/python/getting-started/ for detailed instructions.**
