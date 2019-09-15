"""
Sold houses data
"""
import traceback
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sys
from tqdm import tqdm

logger = logging.getLogger()


def main(args):

    hemnet_url = "https://www.hemnet.se/"
    solna_sold_url = "https://www.hemnet.se/salda/bostader?location_ids%5B%5D=18028&item_types%5B%5D=bostadsratt"

    if not args.debug:
        start_soup = get_soup(solna_sold_url)

        # Get the total number of pages
        page_nrs = start_soup.find("div", {"class": "pagination"})
        page_nrs = max([int(a.text) for a in page_nrs.find_all("a")[:-1]])
    else:
        page_nrs = 1

    data = get_data(solna_sold_url, pages=page_nrs)

    df = pd.DataFrame(data)
    if args.debug:
        print(df.to_string)

    df.to_csv("listings.csv")


def get_sold_listing_data(result):
    try:
        listing = dict()

        # URL
        listing["link"] = result.find("a", {"class": "item-link-container"})["href"]

        # Location data
        location = result.find("div", {"class": "sold-property-listing__location"})
        try:
            location_adress, location_area = location.find_all("span", {"class": "item-link"})
            listing["location_area"] = location_area.text.strip().strip(",")
        except ValueError:
            location_adress = location.find("span", {"class": "item-link"})
            listing["location_area"] = None

        try:
            listing["location_adress"], listing["floor"] = location_adress.text.strip().split(",")
            listing["floor"] = "/".join(filter(str.isdigit, listing["floor"]))
        except ValueError:
            listing["location_adress"] = location_adress.text.strip()
            listing["floor"] = None

        # Remove street nr form adress
        listing["location_street"] = " ".join(listing["location_adress"].split(" ")[:-1])

        # Price data
        price = result.find("div", {"class": "sold-property-listing__price"})
        listing["price_end"] = price.find("span", {"class": "sold-property-listing__subheading"}).text.strip()
        listing["price_end"] = int(listing["price_end"].replace("\xa0", "").strip("Slutpris ").strip(" kr"))

        sold_date = result.find("div", {"class": "sold-property-listing__sold-date"}).text.strip().strip("Såld ")
        listing["sold_day"], listing["sold_month"], listing["sold_year"] = sold_date.split(" ")

        try:
            listing["price_change"] = result.find("div", {"class": "sold-property-listing__price-change"}).contents[0]
            listing["price_change"] = int(listing["price_change"].strip().strip("+").strip("\xa0%"))
        except (AttributeError, ValueError):
            listing["price_change"] = 0

        size = result.find("div", {"class": "sold-property-listing__size"})
        size = size.find("div", {"class": "sold-property-listing__subheading"}).text.strip()
        try:
            listing["size"], _, listing["rooms"] = size.split("\n")
            listing["rooms"] = float(listing["rooms"].strip().strip("\xa0rum").replace(",", "."))
        except ValueError:
            listing["size"] = size
            listing["rooms"] = None

        listing["size"] = float(listing["size"].strip("\xa0m²").replace(",", "."))

        try:
            listing["fee"] = int(result.find("div", {"class": "sold-property-listing__fee"}).text.strip().replace("\xa0", "").strip("kr/mån"))
        except AttributeError:
            listing["fee"] = None

        try:
            listing["price_per_m2"] = int(
                result.find("div", {"class": "sold-property-listing__price-per-m2"}).text.strip().strip(" kr/m²").replace(
                    "\xa0", ""))
        except AttributeError:
            listing["price_per_m2"] = int(listing["price_end"] / listing["size"])

        listing["fee_per_m2"] = float(listing["fee"] / listing["size"])

    except Exception as e:
        print(result)
        logging.error(traceback.format_exc())
        sys.exit(e)

    return listing


def get_sold_listings(soup):
    listings = list()
    for result in get_sold_results(soup):
        listings.append(get_sold_listing_data(result))
    return listings


def get_sold_results(soup):
    return soup.find_all("div", {"class": "sold-property-listing"})


def get_data(url, pages=1):
    data = list()
    for soup in results_pages(url, pages=pages):
        data += get_sold_listings(soup)
    return data


def results_pages(url, pages=1):
    for page_nr in tqdm(range(1, pages+1), desc="Page", unit="page"):
        extension = f"&page={page_nr}"
        yield get_soup(url + extension)


def get_soup(url):
    page = requests.get(url)
    html = page.text
    return BeautifulSoup(html, "html.parser")


def add_arguments(parser):
    parser.add_argument('--debug', default=False, action="store_true")

