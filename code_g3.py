import csv
import logging
from datetime import datetime
from jobspy import scrape_jobs
import pandas as pd

def configure_logging():
    """Set up basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('job_scraper.log'),
            logging.StreamHandler()
        ]
    )

def scrape_job_listings(search_params):
    """
    Scrape job listings based on provided parameters
    Args:
        search_params (dict): Dictionary containing search parameters
    Returns:
        pd.DataFrame: DataFrame containing scraped job listings
    """
    try:
        logging.info(f"Starting job scraping with parameters: {search_params}")
        
        jobs = scrape_jobs(
            site_name=search_params['site_names'],
            search_term=search_params['search_term'],
            google_search_term=search_params['google_search_term'],
            location=search_params['location'],
            results_wanted=search_params['results_wanted'],
            hours_old=search_params['hours_old'],
            country_indeed=search_params['country_indeed']
        )
        
        logging.info(f"Successfully scraped {len(jobs)} jobs")
        return jobs
    
    except Exception as e:
        logging.error(f"Error during job scraping: {str(e)}")
        raise

def clean_job_data(jobs_df):
    """
    Clean and preprocess the scraped job data
    Args:
        jobs_df (pd.DataFrame): Raw job data
    Returns:
        pd.DataFrame: Cleaned job data
    """
    # Remove duplicate jobs based on job URL
    initial_count = len(jobs_df)
    jobs_df.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
    logging.info(f"Removed {initial_count - len(jobs_df)} duplicate jobs")
    
    # Convert date columns to datetime
    if 'date_posted' in jobs_df.columns:
        jobs_df['date_posted'] = pd.to_datetime(jobs_df['date_posted'], errors='coerce')
    
    # Clean salary information
    if 'salary' in jobs_df.columns:
        jobs_df['salary'] = jobs_df['salary'].str.replace('\n', ' ').str.strip()
    
    return jobs_df

def analyze_job_data(jobs_df):
    """
    Perform basic analysis on the job data
    Args:
        jobs_df (pd.DataFrame): Cleaned job data
    Returns:
        dict: Dictionary containing analysis results
    """
    analysis = {}
    
    analysis['total_jobs'] = len(jobs_df)
    
    if 'company' in jobs_df.columns:
        analysis['top_companies'] = jobs_df['company'].value_counts().head(5).to_dict()
    
    if 'date_posted' in jobs_df.columns:
        analysis['newest_job'] = jobs_df['date_posted'].max()
        analysis['oldest_job'] = jobs_df['date_posted'].min()
    
    return analysis

def save_jobs_to_csv(jobs_df, filename):
    """
    Save job data to CSV file with proper formatting
    Args:
        jobs_df (pd.DataFrame): Job data to save
        filename (str): Output filename
    """
    try:
        jobs_df.to_csv(
            filename,
            quoting=csv.QUOTE_NONNUMERIC,
            escapechar="\\",
            index=False,
            encoding='utf-8'
        )
        logging.info(f"Successfully saved job data to {filename}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {str(e)}")
        raise

def main():
    """Main function to execute the job scraping workflow"""
    configure_logging()
    
    # Define search parameters
    search_params = {
        'site_names': ["indeed", "linkedin"],
        'search_term': "data analyst",
        'google_search_term': "data analyst",
        'location': "Paris",
        'results_wanted': 40,
        'hours_old': 72,
        'country_indeed': 'France'
    }
    
    try:
        # Step 1: Scrape job listings
        jobs = scrape_job_listings(search_params)
        
        # Step 2: Clean and preprocess data
        cleaned_jobs = clean_job_data(jobs)
        
        # Step 3: Perform basic analysis
        analysis_results = analyze_job_data(cleaned_jobs)
        
        # Log analysis results
        logging.info("\nJob Data Analysis Results:")
        for key, value in analysis_results.items():
            logging.info(f"{key.replace('_', ' ').title()}: {value}")
        
        # Step 4: Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"jobs_{timestamp}.csv"
        save_jobs_to_csv(cleaned_jobs, output_filename)
        
        # Display sample data
        logging.info("\nSample Job Data:")
        logging.info(cleaned_jobs.head(10).to_string())
        
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
