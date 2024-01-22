# Indeed Job Scraper
This Python script allows you to scrape job data from Indeed for a specific job position and location. 
It utilizes Selenium for web scraping and BeautifulSoup for parsing HTML content. The script supports multiple countries and is capable of sending job results via email in CSV format. Additionally, the script takes screenshots of the job search results.


### Prerequisites
Before using the script, make sure you have the following installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Chrome browser](https://www.google.com/chrome/)
- [ChromeDriver](https://chromedriver.chromium.org/downloads)


### Installation
1. Ensure you have Python 3.x installed. Use the following command to install the required dependencies:
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
This above command will install the requirements from the requirements.txt file

### Usage
1. ```bash
   git clone https://github.com/your-username/indeed-job-scraper.git

Go to the IndeedJobScraper directory by typing: cd IndeedJobScraper
   
2. Modify the script variables:
- country: Set the desired country URL.
- receiver_email: Provide the email address where job results should be sent.
- job_position: Specify the job position you are looking for.
- job_location: Specify the job location.

3. Run the script:
   ```bash
   python main.py

### Results
The script will generate a CSV file with the job results, take screenshots of the job search results, and send the results to the specified email address.
If no results are found, an email will be sent with suggestions for refining the search criteria. The email content is customized.

### Note: 
The script uses a headless Chrome browser for web scraping, and it may be necessary to update the ChromeDriver version based on your Chrome browser version.
Make sure to replace the placeholder email addresses and passwords in the script with your own credentials.
To enable the send email feature, follow the instructions in this link: [How to Generate an App Password](https://support.google.com/mail/thread/205453566/how-to-generate-an-app-password?hl=en).
Use this script responsibly.
