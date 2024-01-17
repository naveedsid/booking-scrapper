import scrapy
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from booking.items import PropertiesItem
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


class PropertiesSpider(scrapy.Spider):
    name = "properties"
    # allowed_domains = ["booking.com"]
    # start_urls = ["https://www.booking.com/"]

    def start_requests(self):
        options = uc.ChromeOptions()
        # options.add_argument("--headless")
        driver = uc.Chrome(options=options)
        # options.headless = True
        driver.get("""https://www.booking.com/searchresults.html?aid=356980&label=gog235jc-1DCAsoZUInZHVicm92bmlrLW9sZC10b3duLWFwYXJ0bWVudHMtZHVicm92bmlrSDNYA2hliAEBmAExuAEXyAEP2AED6AEB-AECiAIBqAIDuALY9uSkBsACAdICJDBlNDY0YzdmLThjODItNDFjZS1iZWExLTViYjA1Mzk3NGM0YdgCBOACAQ&sid=ae741f093fcd9b8ff99674dc81fc15b2&sb=1&sb_lp=1&src=theme_landing_city&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Fapartments%2Fcity%2Fhr%2Fdubrovnik.html%3Faid%3D356980%26label%3Dgog235jc-1DCAsoZUInZHVicm92bmlrLW9sZC10b3duLWFwYXJ0bWVudHMtZHVicm92bmlrSDNYA2hliAEBmAExuAEXyAEP2AED6AEB-AECiAIBqAIDuALY9uSkBsACAdICJDBlNDY0YzdmLThjODItNDFjZS1iZWExLTViYjA1Mzk3NGM0YdgCBOACAQ%26sid%3Dae741f093fcd9b8ff99674dc81fc15b2%26&top_ufis=0&theme_id=1&theme_source=theme_landing_city&ss=Old+Town%2C+Dubrovnik%2C+Dubrovnik-Neretva+County%2C+Croatia&is_ski_area=&ssne=Dubrovnik&ssne_untouched=Dubrovnik&checkin_year=&checkin_month=&checkout_year=&checkout_month=&efdco=1&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&ss_raw=old+town+du&ac_position=0&ac_langcode=en&ac_click_type=b&ac_meta=GhA2NjAyMzMzMDQyYTEwN2JjIAAoATICZW46C29sZCB0b3duIGR1QABKAFAA&dest_id=1915&dest_type=district&place_id_lat=42.64074&place_id_lon=18.109398&search_pageview_id=6602333042a107bc&search_selected=true&search_pageview_id=6602333042a107bc&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0""")
        time.sleep(5)
        driver.maximize_window()
        time.sleep(1)
        
        try:
            sign_in_dialog = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.b2bfde3841[role='dialog']")))
            if sign_in_dialog.is_displayed():
                dialog_close_btn = driver.find_element(By.XPATH,"//div[contains(@class, 'b2bfde3841') and contains(@role, 'dialog')]//button[contains(@aria-label, 'Dismiss')]")
                dialog_close_btn.click()
                time.sleep(2)
        except:
            pass
        # div.b2bfde3841[role='dialog']
        # div.b2bfde3841[role='dialog'] button[aria-label = 'Dismiss sign-in info.']

        no_of_pages = 2
        for i in range(no_of_pages):
            properties_links = driver.find_elements(By.CSS_SELECTOR,"h3.a4225678b2 a")
            for properties_link in properties_links:
                properties_link_href = properties_link.get_attribute("href")
                # print(properties_link_href)
                yield scrapy.Request(url=properties_link_href, callback=self.parse, meta={'properties_link_href': properties_link_href})
            #----- Pagination --------
            next_btn = driver.find_element(By.CSS_SELECTOR,"button[aria-label='Next page']")
            next_btn.click()
            time.sleep(10)
            #--------------- Wait for JS Loading ---------------
            # WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='overlay-spinner']")))
        
        # next_page_url = driver.current_url
        # yield scrapy.Request(url=next_page_url, callback=self.parse)
      
        driver.quit()

    def parse(self, response):
        # print(response.text)
        item = PropertiesItem()
        item['url'] = response.meta.get('properties_link_href')
        item['title'] = response.css('h2.pp-header__title::text').get()
        item['address'] = response.css('span.hp_address_subtitle::text').get().strip('\n')
        item['rating_value'] = response.css("div[data-testid='review-score-right-component'] div::text").get()
        item['review_count'] = response.css("div.d8eab2cf7f.c90c0a70d3.db63693c62::text").get()
        
        #-------- Beds -------------
        total_beds = []
        total_beds_str = []

        #---------- Types of Beds ----------
        single_bed = []
        double_bed = []
        large_double_bed = []
        extra_large_double_bed = []
        futon_bed = []
        sofa_bed = []
        bunk_bed = []
        unknown = []

        all_beds = response.css("span.c58eea6bdb::text").getall()
        for sin_bed in all_beds:
            sin_bed_list = sin_bed.split(" ")

            if sin_bed_list[1] in ["twin", "single"]:
                single_bed.append(int(sin_bed_list[0]))
            elif sin_bed_list[1] in ["full", "double"]:
                double_bed.append(int(sin_bed_list[0]))
            elif sin_bed_list[1] in ["queen", "large"]:
                large_double_bed.append(int(sin_bed_list[0]))
            elif sin_bed_list[1] in ["king", "extra-large"]:
                extra_large_double_bed.append(int(sin_bed_list[0]))
            elif sin_bed_list[1] in ["futon"]:
                futon_bed.append(int(sin_bed_list[0]))
            elif sin_bed_list[1] in ["sofa"]:
                sofa_bed.append(int(sin_bed_list[0]))
            elif sin_bed_list[1] in ["bunk"]:
                bunk_bed.append(int(sin_bed_list[0]))
            else:
                print("*********************************")
                print(sin_bed_list[1])
                unknown.append(int(sin_bed_list[0]))
                print(response.meta.get('properties_link_href'))
                print(response.css('h2.pp-header__title::text').get())
                print(sin_bed_list)
                print("*********************************")
        
        bed_final_res_list = []
        if single_bed:
            bed_final_res_list.append(f"{sum(single_bed)} Single Bed")
        if double_bed:
            bed_final_res_list.append(f"{sum(double_bed)} Double Bed")
        if large_double_bed:
            bed_final_res_list.append(f"{sum(large_double_bed)} Large Double Bed")
        if extra_large_double_bed:
            bed_final_res_list.append(f"{sum(extra_large_double_bed)} Extra Large Double Bed")
        if futon_bed:
            bed_final_res_list.append(f"{sum(futon_bed)} Futon Bed")
        if sofa_bed:
            bed_final_res_list.append(f"{sum(sofa_bed)} Sofa Bed")
        if bunk_bed:
            bed_final_res_list.append(f"{sum(bunk_bed)} Bunk Bed")
        if unknown:
            bed_final_res_list.append(f"{sum(unknown)} Unknown")
        
        bed_final_res = ', '.join(bed_final_res_list)
            

        item['beds'] = bed_final_res

        #----- All Beds Sum -------------
        all_beds_sum = 0
        beds_types_names = [single_bed, double_bed, large_double_bed, extra_large_double_bed, futon_bed, sofa_bed, unknown]
        for sin_bed_list in beds_types_names:
            sin_bed_sum_int = sum(sin_bed_list)
            all_beds_sum += sin_bed_sum_int
        item['beds_all'] = all_beds_sum
    
        total_guests_s = []
        guests = response.css('div.ace2775fec.be781dfdd4')
        for guest in guests:
            adult_text_list = guest.attrib['aria-label'].split(' ')
            adult_text_num = [s for s in adult_text_list if s.isdigit()]
            total_guests_s.extend(adult_text_num)
            total_guests = [eval(i) for i in total_guests_s]
            total_guests = sum(total_guests)
        item['num_of_guests'] = total_guests

        item['accomodation_type'] = str(len(guests)) + " Apartments"

        location = response.css("a#hotel_sidebar_static_map").attrib['data-atlas-latlng'].split(',')
        # latlnglist = location.split(",")
        # //a[@id='hotel_sidebar_static_map']/@data-atlas-latlng
        item['latitude'] = location[0]
        item['longitude'] = location[1]

        yield item
