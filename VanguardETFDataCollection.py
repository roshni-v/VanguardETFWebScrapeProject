import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

'''
These following two functions handle situations where the program tries to access a webpage field that hasn't been loaded yet. 
They ensure that the program continues trying until the field becomes available. 
'''
def get_element_text_not_dash(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        if ((element is None) or (element.text == '—')):
            print('retrying 1')
            time.sleep(0.5)
            return get_element_text_not_dash(driver, xpath)
        else:    
            return element.text
    except:
        print('retrying 1')
        time.sleep(0.5)
        return get_element_text_not_dash(driver, xpath)
    
def get_element_text(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        if (element is None):
            print('retrying 2') 
            time.sleep(0.5)
            return get_element_text(driver, xpath)
        else:    
            return element.text
    except:
        print('retrying 2')
        time.sleep(0.5)
        return get_element_text(driver, xpath)   

def main():
    url = "https://investor.vanguard.com/investment-products/list/etfs?view=detail"
    options = Options()
    options.add_argument('--headless')

    data = []

    with webdriver.Firefox(options=options) as driver:

        # Interate through the ETF list that spans two pages and retrieves each ETF's individual link
        driver.get(url)
        time.sleep(1.5)
        page1 = driver.page_source
        soup = BeautifulSoup(page1, 'html.parser')
        container = soup.find_all('a', attrs={'class': 'vui-text-secondary-link'})
        button = driver.find_element(By.XPATH, '//*[@id="next-page-btn"]')
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1.5)
        page2 = driver.page_source
        soup = BeautifulSoup(page2, 'html.parser')
        container.extend(soup.find_all('a', attrs={'class': 'vui-text-secondary-link'}))

        etf_links = [a.get('href') for a in container]
    
        # Fetch data for each ETF
        for etf_link in etf_links:
            driver.get(etf_link)
            time.sleep(1)
            name = etf_link.split("https://investor.vanguard.com/investment-products/etfs/profile/", 1)[1]
            risk_reward_scale = get_element_text_not_dash(driver, '//*[@id="Dashboard"]/div[2]/div/div[2]/dashboard-stats/div/div[2]/div[2]/div/risk-scale/div/div[1]')
            asset_class = get_element_text_not_dash(driver, '/html/body/vmf-root/profile/div/dashboard/section/div[2]/div/div[2]/dashboard-stats/div/div[1]/div[2]/h4')
            category = get_element_text_not_dash(driver, '/html/body/vmf-root/profile/div/dashboard/section/div[2]/div/div[2]/dashboard-stats/div/div[2]/div[1]/h4')
            expense_ratio = get_element_text_not_dash(driver, '/html/body/vmf-root/profile/div/dashboard/section/div[2]/div/div[2]/dashboard-stats/div/div[3]/div[1]/h4')
            market_price = get_element_text_not_dash(driver, '/html/body/vmf-root/profile/div/dashboard/section/div[2]/div/div[2]/dashboard-stats/div/div[4]/div[1]/h4[1]')
            inception_date = get_element_text_not_dash(driver, '//*[@id="overview_section"]/div/div[1]/div[1]/key-facts/div/div/table/tbody/tr[6]/td/p')
            ytd = get_element_text(driver, '//*[@id="performance-fees_section"]/div[1]/div[2]/div[2]/performance-summary/div/div[3]/div/table/tbody/tr[1]/td[3]')
            y1 = get_element_text(driver, '//*[@id="performance-fees_section"]/div[1]/div[2]/div[2]/performance-summary/div/div[3]/div/table/tbody/tr[1]/td[4]')
            y3 = get_element_text(driver, '//*[@id="performance-fees_section"]/div[1]/div[2]/div[2]/performance-summary/div/div[3]/div/table/tbody/tr[1]/td[5]')
            y5 = get_element_text(driver, '//*[@id="performance-fees_section"]/div[1]/div[2]/div[2]/performance-summary/div/div[3]/div/table/tbody/tr[1]/td[6]')
            y10 = get_element_text(driver, '//*[@id="performance-fees_section"]/div[1]/div[2]/div[2]/performance-summary/div/div[3]/div/table/tbody/tr[1]/td[7]')
            since_inception = get_element_text_not_dash(driver, '//*[@id="performance-fees_section"]/div[1]/div[2]/div[2]/performance-summary/div/div[3]/div/table/tbody/tr[1]/td[8]')
            avg_volume_25days = get_element_text_not_dash(driver, '//*[@id="price_section"]/div[2]/app-closing-price/div[2]/div/div[10]/div/h4')
            avg_volume_50days = get_element_text_not_dash(driver, '//*[@id="price_section"]/div[2]/app-closing-price/div[2]/div/div[11]/div/h4')
            num_of_stocks_or_bonds = get_element_text_not_dash(driver, "//td[contains(text(),'Number of')]/following::td")
            fundtotalnetassets = get_element_text_not_dash(driver, "//td[contains(text(),'Fund total net assets')]/following::td")

            bodyText = driver.find_element(By.XPATH, '//body').text
            if "Number of bonds" in bodyText:
                pe_ratio = None
            else:
                pe_ratio = get_element_text_not_dash(driver, "//a[contains(text(),'P/E ratio')]/following::td")

            subdata = [
                name, risk_reward_scale, asset_class, category, expense_ratio,
                market_price, inception_date, ytd, y1, y3, y5, y10, since_inception,
                avg_volume_25days, avg_volume_50days, num_of_stocks_or_bonds, pe_ratio, fundtotalnetassets
            ]
            print(subdata)
            data.append(subdata)

    # Create a DataFrame from collected data and save it to a CSV file
    dataFrame = pd.DataFrame(data=data, columns=["ETF Name", "Risk/Reward Value", "Asset Class", "Category", "Expense Ratio", "Market Price", "Inception Date", "YTD % Return", "1 Year % Return", "3 Year % Return", "5 Year % Return", "10 Year % Return", "% Return Since Inception", "25-day Avg Volume", "50-day Avg Volume", "# of Stocks/Bonds", "P/E Ratio", "Fund Total Net Assets"])
    dataFrame.to_csv(r'D:/etfs.csv', index=False)

if __name__ == "__main__":
    main()
