import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

"""
List of countries url.
"""
nigeria = 'https://ng.indeed.com'
united_kingdom = 'https://uk.indeed.com'
united_states = 'https://www.indeed.com'
canada = 'https://ca.indeed.com'
germany = 'https://de.indeed.com'
australia = 'https://au.indeed.com'
south_africa = 'https://za.indeed.com'
sweden = 'https://se.indeed.com'
singapore = 'https://www.indeed.com.sg'
switzerland = 'https://www.indeed.ch'
united_arab_emirates = 'https://www.indeed.ae'
new_zealand = 'https://nz.indeed.com'
india = 'https://www.indeed.co.in'
france = 'https://www.indeed.fr'
italy = 'https://it.indeed.com'
spain = 'https://www.indeed.es'
japan = 'https://jp.indeed.com'
south_korea = 'https://kr.indeed.com'
brazil = 'https://www.indeed.com.br'
mexico = 'https://www.indeed.com.mx'
china = 'https://cn.indeed.com'
saudi_arabia = 'https://sa.indeed.com'
egypt = 'https://eg.indeed.com'
thailand = 'https://th.indeed.com'
vietnam = 'https://vn.indeed.com'
argentina = 'https://ar.indeed.com'
ireland = 'https://ie.indeed.com'

global total_jobs


def configure_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


def search_jobs(driver, country, job_position, job_location, date_posted):
    full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'
    print(full_url)
    driver.get(full_url)

    job_count_element = driver.find_element(By.XPATH,
                                            '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')
    if job_count_element:
        global total_jobs
        total_jobs = job_count_element.find_element(By.XPATH, './span').text
        print(f"{total_jobs} found")
    driver.save_screenshot('screenshot.png')
    return full_url


def scrape_job_data(driver, country):
    df = pd.DataFrame({'Link': [''], 'Job Title': [''], 'Company': [''],
                       'Date Posted': [''], 'Location': ['']})
    job_count = 0
    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')

        boxes = soup.find_all('div', class_='job_seen_beacon')

        for i in boxes:
            link = i.find('a').get('href')
            link_full = country + link
            job_title = i.find('a', class_='jcs-JobTitle css-jspxzf eu4oa1w0').text
            # Check if the 'Company' attribute exists
            company_tag = i.find('span', {'data-testid': 'company-name'})
            company = company_tag.text if company_tag else None

            date_posted = i.find('span', class_='date').text
            location_element = i.find('div', {'data-testid': 'text-location'})
            location = ''
            if location_element:
                # Check if the element contains a span
                span_element = location_element.find('span')

                if span_element:
                    location = span_element.text
                else:
                    location = location_element.text

            new_data = pd.DataFrame({'Link': [link_full], 'Job Title': [job_title],
                                     'Company': [company],
                                     'Date Posted': [date_posted],
                                     'Location': [location]})

            df = pd.concat([df, new_data], ignore_index=True)
            job_count += 1

        print(f"Scraped {job_count} of {total_jobs}")

        try:
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')

            next_page = country + next_page
            driver.get(next_page)

        except:
            break

    return df


def clean_data(df):
    def posted(x):
        x = x.replace('PostedPosted', '').strip()
        x = x.replace('EmployerActive', '').strip()
        x = x.replace('PostedToday', '0').strip()
        x = x.replace('today', '0').strip()

        return x

    def day(x):
        x = x.replace('days ago', '').strip()
        x = x.replace('day ago', '').strip()
        return x

    def plus(x):
        x = x.replace('+', '').strip()
        return x

    df['Date Posted'] = df['Date Posted'].apply(posted)
    df['Date Posted'] = df['Date Posted'].apply(day)
    df['Date Posted'] = df['Date Posted'].apply(plus)

    return df


def sort_data(df):
    def convert_to_integer(x):
        try:
            return int(x)
        except ValueError:
            return float('inf')

    df['Date_num'] = df['Date Posted'].apply(lambda x: x[:2].strip())
    df['Date_num2'] = df['Date_num'].apply(convert_to_integer)
    df.sort_values(by=['Date_num2'], inplace=True)

    df = df[['Link', 'Job Title', 'Company', 'Date Posted', 'Location']]
    return df


def save_csv(df, job_position, job_location):
    def get_user_desktop_path():
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        return desktop_path

    file_path = os.path.join(get_user_desktop_path(), '{}_{}'.format(job_position, job_location))
    csv_file = '{}.csv'.format(file_path)
    df.to_csv('{}.csv'.format(file_path), index=False)

    return csv_file


def send_email(df, receiver_email, job_position, job_location):
    sender = 'sender@gmail.com'
    receiver = receiver_email
    msg = MIMEMultipart()
    msg['Subject'] = 'New Jobs from Indeed'
    msg['From'] = sender
    msg['To'] = ','.join(receiver)

    attachment_filename = generate_attachment_filename(job_position, job_location)

    csv_content = df.to_csv(index=False).encode()

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(csv_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
    msg.attach(part)

    s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    s.login(user=sender, password='123456')

    s.sendmail(sender, receiver, msg.as_string())

    s.quit()


def send_email_empty(sender, receiver_email, subject, body):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join(receiver_email)

    # Attach the body as the text/plain part of the email
    msg.attach(MIMEText(body, 'plain'))

    s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    s.login(user=sender, password='123456')

    s.sendmail(sender, receiver_email, msg.as_string())

    s.quit()


def generate_attachment_filename(job_title, job_location):
    filename = f"{job_title.replace(' ', '_')}_{job_location.replace(' ', '_')}.csv"
    return filename


def main():
    driver = configure_webdriver()
    country = united_states
    receiver_email = 'receiver@gmail.com'
    job_position = 'content writer'
    job_location = 'remote'
    date_posted = 7

    sorted_df = None

    try:
        full_url = search_jobs(driver, country, job_position, job_location, date_posted)
        df = scrape_job_data(driver, country)

        if df.shape[0] == 1:
            print("No results found. Something went wrong.")
            sender = 'sender@gmail.com'
            subject = 'No Jobs Found on Indeed'
            body = """
            No jobs were found for the given search criteria.
            Please consider the following:
            1. Try adjusting your search criteria.
            2. If you used English search keywords for non-English speaking countries,
               it might return an empty result. Consider using keywords in the country's language.
            3. Try more general keyword(s), check your spelling or replace abbreviations with the entire word

            Feel free to try a manual search with this link and see for yourself:
            Link {}
            """.format(full_url)

            send_email_empty(sender, receiver_email, subject, body)
        else:
            cleaned_df = clean_data(df)
            sorted_df = sort_data(cleaned_df)
            # csv_file = save_csv(sorted_df, job_position, job_location)
    finally:
        try:
            if sorted_df is not None:
                send_email(sorted_df, receiver_email, job_position, job_location)
        except Exception as e:
            print(f"Error sending email: {e}")
        finally:
            pass
            driver.quit()


if __name__ == "__main__":
    main()
