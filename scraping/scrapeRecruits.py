import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def parse_location(location):
    try:
        # Find the position of the last opening parenthesis
        last_paren = location.rfind("(")
        # Split the location into school and hometown/state
        school = location[:last_paren].strip()
        hometown = location[last_paren + 1:].strip(")")
        
        # Split city and state
        city, state = hometown.split(", ")
        return school, city, state
    except Exception as e:
        return location, "", ""
    
# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

# Define the CSV file name
csv_filename = "recruits20-25.csv"

# Open the CSV file in write mode
with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Loop over the years from 2000 to 2025
    for year in range(2000, 2026):
        # Define URL for the current year
        url = f"https://247sports.com/season/{year}-football/CompositeRecruitRankings/?InstitutionGroup=HighSchool"

        # Navigate to the URL
        driver.get(url)

        # Retrieve the current URL
        get_url = driver.current_url

        # Wait until the URL matches
        wait.until(EC.url_to_be(url))

        # Click all "Show More" buttons until they are no longer found
        while True:
            try:
                # Wait for the "Show More" button to appear
                show_more_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@data-js='showmore']")))
                driver.execute_script("arguments[0].scrollIntoView();", show_more_button)

                # Click the "Show More" button
                driver.execute_script("arguments[0].click();", show_more_button)

                # Wait for the loading div to appear and then disappear
                wait.until(EC.presence_of_element_located((By.ID, "global-loading")))
                wait.until(EC.invisibility_of_element_located((By.ID, "global-loading")))
            # Move on once the show more button no longer shows up
            except Exception as e:
                # Print the exception details
                print("An exception occurred:")
                print(str(e))
                traceback.print_exc()
                break

        # After all "Show More" buttons are clicked, find all recruit elements
        recruits = driver.find_elements(By.XPATH, "//li[@class='rankings-page__list-item']")

        # List to hold all the rows for the current year
        rows = []

        # Accumulate the data for each recruit
        for recruit in recruits:
            name = recruit.find_element(By.XPATH, ".//a[@class='rankings-page__name-link']").text
            position = recruit.find_element(By.XPATH, ".//div[@class='position']").text
            rating = recruit.find_element(By.XPATH, ".//span[@class='score']").text
            
            # Check the status div for either the img-link a tag or the rankings-page__crystal-ball div
            status_div = recruit.find_element(By.XPATH, ".//div[@class='status']")
            img_link = status_div.find_elements(By.XPATH, ".//a[@class='img-link']")
            crystal_ball = status_div.find_elements(By.XPATH, ".//div[@class='rankings-page__crystal-ball']")
            
            if img_link:
                # Get the committed team from the img-link a tag
                teamImage = img_link[0].find_element(By.XPATH, ".//img")
                committedTeam = teamImage.get_attribute("title")
            elif crystal_ball:
                # Set committedTeam to "uncommitted" if crystal ball indicator is found
                committedTeam = "Uncommitted"
            else:
                committedTeam = "Unknown"  # In case neither is found
            
            location = recruit.find_element(By.XPATH, ".//span[@class='meta']").text
            school, city, state = parse_location(location)
            print(f'year: {year}\n name: {name}\n position: {position}\n rating: {rating}\n committedTeam: {committedTeam}\n school: {school}\n city: {city}\n state: {state}')
            # Add the row to the list
            rows.append([year, name, position, rating, committedTeam, school, city, state])

        # Write all accumulated rows to the CSV at once
        writer.writerows(rows)

# Close the WebDriver after all years are processed
driver.quit()