from bs4 import BeautifulSoup
import requests
import io
from util import separate_by_br, convert_checkmark, parse_price, get_image_links, parse_hybridization_children, parse_months, parse_variations, parse_source, parse_image_URLs, parse_rose_image_URLs, dump_data


URLS = {
    # --- New Horizons ---
    # Characters
    "villagers": "https://animalcrossing.fandom.com/wiki/Villager_list_(New_Horizons)",

    # Museum
    "fish": "https://animalcrossing.fandom.com/wiki/Fish_(New_Horizons)",
    "bugs": "https://animalcrossing.fandom.com/wiki/Bugs_(New_Horizons)",
    "fossils": "https://animalcrossing.fandom.com/wiki/Fossils_(New_Horizons)",
    "artworks": "https://animalcrossing.fandom.com/wiki/Artwork_(New_Horizons)",

    # Crafting
    "tools": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Tools",
    "housewares": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Housewares",
    "miscellaneous": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Miscellaneous",
    "equipments": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Equipment",
    "others": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Other",
    "wallMounteds": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Wall-mounted",
    "wallpaperRugsFloorings": "https://animalcrossing.fandom.com/wiki/DIY_recipes/Wallpaper,_rugs_and_flooring",

    # Clothing
    "tops": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Tops",
    "bottoms": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Bottoms",
    "dresses": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Dresses",
    "hats": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Hats",
    "accessories": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Accessories",
    "socks": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Socks",
    "shoes": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Shoes",
    "bags": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Bags",
    "umbrellas": "https://animalcrossing.fandom.com/wiki/Clothing_(New_Horizons)/Umbrellas",
    
    # Furnitures
    "furniture_housewares": "https://animalcrossing.fandom.com/wiki/Furniture_(New_Horizons)/Housewares",
    
    # Flowers
    "flowers": "https://animalcrossing.fandom.com/wiki/Flower/New_Horizons_mechanics"
    # --- New Leaf ---
    # "fish": "https://animalcrossing.fandom.com/wiki/Fish_(New_Leaf)",
    # "bugs": "https://animalcrossing.fandom.com/wiki/Bugs_(New_Leaf)",
}


def scrape_villagers(key):
    # get list of villager urls
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup("table", {"class": "sortable"})
    villagers_urls = []
    for tr in table[0]("tr")[1:]:
        villagers_urls.append("https://animalcrossing.fandom.com" + tr("td")[0].a.get("href"))
    # scrape each villager page
    villagers_info = {}
    for vu in villagers_urls:
        response = requests.get(vu, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        asides = soup("aside")
        name = asides[0]("h2")[0].text
        item = {}
        item["image_url"] = asides[0]("img")[0].get("src").replace("/scale-to-width-down/350", "")
        if len(asides[0]("figcaption")) > 0:
            item["caption"] = asides[0]("figcaption")[0].text
        else:
            item["caption"] = None
        for div in asides[0]("div", {"class": "pi-item"}):
            if div.find("div").text == "Unknown":
                item[div("h3")[0].text.lower().replace(" ", "_")] = None
            else:
                item[div("h3")[0].text.lower().replace(
                    " ", "_")] = div.find("div").text
        villagers_info[name] = item
    dump_data(villagers_info, "characters/villagers")

def scrape_bugs(key):  # take url and return object containing bugs data
    url = URLS.get(key)
    # create soup object
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    # find the target table
    table = soup.find_all("table", {"class": "sortable"})
    items = {}
    # go through each tr in the table, ignoring the table header
    for tr in table[0].find_all("tr")[1:]:
        tableData = []
        # get rid of empty space
        for td in tr.find_all("td"):
            tableData.append(td.next.strip())
        # scrape each item
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
            "imageLink": tr.find_all("a")[1]['href'],
            "price": int(tableData[2]),
            "location": tr.find_all("td")[3].text.strip('\n').strip(),
            "time": tr.find_all("small")[0].text,
            "seasonsNorthernHemisphere": {
                "jan": convert_checkmark(tableData[5]),
                "feb": convert_checkmark(tableData[6]),
                "mar": convert_checkmark(tableData[7]),
                "apr": convert_checkmark(tableData[8]),
                "may": convert_checkmark(tableData[9]),
                "jun": convert_checkmark(tableData[10]),
                "jul": convert_checkmark(tableData[11]),
                "aug": convert_checkmark(tableData[12]),
                "sep": convert_checkmark(tableData[13]),
                "oct": convert_checkmark(tableData[14]),
                "nov": convert_checkmark(tableData[15]),
                "dec": convert_checkmark(tableData[16])
            },
            "seasonsSouthernHemisphere": {  # shift northern hemisphere by 6 months
                "jan": convert_checkmark(tableData[11]),
                "feb": convert_checkmark(tableData[12]),
                "mar": convert_checkmark(tableData[13]),
                "apr": convert_checkmark(tableData[14]),
                "may": convert_checkmark(tableData[15]),
                "jun": convert_checkmark(tableData[16]),
                "jul": convert_checkmark(tableData[5]),
                "aug": convert_checkmark(tableData[6]),
                "sep": convert_checkmark(tableData[7]),
                "oct": convert_checkmark(tableData[8]),
                "nov": convert_checkmark(tableData[9]),
                "dec": convert_checkmark(tableData[10])
            }
        }
        # add to the json
        items[name] = item
    dump_data(items, "museum/" + key)
    # return for debugging
    return items


def scrape_fish(key):  # same logic as scrapeBugs
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "sortable"})
    items = {}
    for tr in table[0].find_all("tr")[1:]:
        tableData = []
        for td in tr.find_all("td"):
            tableData.append(td.next.strip())
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
            "imageLink": tr.find_all("a")[1]['href'],
            "price": parse_price(tableData[2]),
            "location": tr.find_all("td")[3].text.strip('\n').strip(),
            "shadowSize": tableData[4],
            "time": tr.find_all("small")[0].text,
            "seasonsNorthernHemisphere": {
                "jan": convert_checkmark(tableData[6]),
                "feb": convert_checkmark(tableData[7]),
                "mar": convert_checkmark(tableData[8]),
                "apr": convert_checkmark(tableData[9]),
                "may": convert_checkmark(tableData[10]),
                "jun": convert_checkmark(tableData[11]),
                "jul": convert_checkmark(tableData[12]),
                "aug": convert_checkmark(tableData[13]),
                "sep": convert_checkmark(tableData[14]),
                "oct": convert_checkmark(tableData[15]),
                "nov": convert_checkmark(tableData[16]),
                "dec": convert_checkmark(tableData[17])
            },
            "seasonsSouthernHemisphere": {
                "jan": convert_checkmark(tableData[12]),
                "feb": convert_checkmark(tableData[13]),
                "mar": convert_checkmark(tableData[14]),
                "apr": convert_checkmark(tableData[15]),
                "may": convert_checkmark(tableData[16]),
                "jun": convert_checkmark(tableData[17]),
                "jul": convert_checkmark(tableData[6]),
                "aug": convert_checkmark(tableData[7]),
                "sep": convert_checkmark(tableData[8]),
                "oct": convert_checkmark(tableData[9]),
                "nov": convert_checkmark(tableData[10]),
                "dec": convert_checkmark(tableData[11])
            }
        }
        items[name] = item
    dump_data(items, "museum/" + key)
    return items


def scrape_fossils(key):  # same logic as scrapeBugs and scrapeFish
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "sortable"})
    items = {}
    # Stand-alone fossils
    for tr in table[0].find_all("tr")[1:]:
        tableData = []
        for td in tr.find_all("td"):
            tableData.append(td.next.strip())
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
            "imageLink": tr.find_all("a")[1]['href'],
            "price": parse_price(tableData[2]),
            "isMultipart": False
        }
        tableData.append(item)
        items[name] = item
    # Multi-part fossils
    for tr in table[1].find_all("tr")[1:]:
        tableData = []
        tds = tr.find_all("td")
        if not tds:
            currentCategory = tr.find_all("a")[0].text
            continue
        for td in tr.find_all("td"):
            tableData.append(td.next.strip())
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
            "imageLink": tr.find_all("a")[1]['href'],
            "price": parse_price(tableData[2]),
            "isMultipart": True,
            "category": currentCategory
        }
        items[name] = item
    dump_data(items, "museum/" + key)
    return items


def scrape_artworks(key):
    url = URLS.get(key)
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "wikitable"})
    items = {}
    for tr in table[0].find_all("tr")[1:]:
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
        }
        if tr.find_all("td")[1].a:
            item["fakeImageLink"] = tr.find_all("td")[1].a['href']
        if tr.find_all("td")[2].a:
            item["realImageLink"] = tr.find_all("td")[2].a['href']
        if tr.find_all("td")[3]:
            item["description"] = tr.find_all("td")[3].text.strip('\n').lstrip()
        items[name] = item
    for tr in table[1].find_all("tr")[1:]:
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
        }
        if tr.find_all("td")[1].a:
            item["fakeImageLink"] = tr.find_all("td")[1].a['href']
        if tr.find_all("td")[2].a:
            item["realImageLink"] = tr.find_all("td")[2].a['href']
        if tr.find_all("td")[3]:
            item["description"] = tr.find_all("td")[3].text.strip('\n').lstrip()
        items[name] = item
    dump_data(items, "museum/" + key)
    return items

def scrape_tools(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "sortable"})
    items = {}
    for tr in table[0].find_all("tr")[1:]:
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
        }
        if tr.find_all("a")[1]['href']:
            item["imageLink"] = tr.find_all("a")[1]['href']
        if tr.find_all("td")[2]:
            item["materials"] = separate_by_br(tr.find_all("td")[2]).lstrip().strip("\n").split(",")
        if tr.find_all("td")[2].find_all("img"):
            item["materialsImageLink"] = get_image_links(tr.find_all("td")[2].find_all("img"))
        if tr.find_all("td")[3].img.get("data-src"):
            item["sizeImageLink"] = tr.find_all("td")[3].img.get("data-src")
        if tr.find_all("td")[4].text:
            item["obtainedFrom"] = tr.find_all("td")[4].text.strip().strip("\n").splitlines()
        if tr.find_all("td")[5]:
            item["price"] = parse_price(tr.find_all("td")[5].text)
        items[name] = item
    dump_data(items, "crafting/" + key)
    return items


def scrape_equipments(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "sortable"})
    items = {}
    for tr in table[0].find_all("tr")[1:]:
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
            "imageLink": tr.find_all("a")[1]['href'],
            "materials": separate_by_br(tr.find_all("td")[2]).lstrip().strip("\n").split(","),
            "materialsImageLink": get_image_links(tr.find_all("td")[2].find_all("img")),
            "sizeImageLink": tr.find_all("td")[3].img.get("data-src"),
            "obtainedFrom": tr.find_all("td")[4].text.strip().strip("\n").splitlines(),
            "price": parse_price(tr.find_all("td")[5].text)
        }
        items[name] = item
    dump_data(items, "crafting/" + key)
    return items


def scrape_wallpapers(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "sortable"})
    items = {}
    for tr in table[0].find_all("tr")[1:]:
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
        }
        if tr.find_all("a")[1]['href']:
            item["imageLink"] = tr.find_all("a")[1]['href']
        if tr.find_all("td")[2]:
            item["materials"] = separate_by_br(
                tr.find_all("td")[2]).strip("\n").split(",")
            item["materialsImageLink"] = get_image_links(
                tr.find_all("td")[2].find_all("img"))
        if tr.find_all("td")[3].find_all("a"):
            item["sizeLink"] = tr.find_all(
                "td")[3].find_all("a")[0]['href']
        if tr.find_all("td")[4].text:
            if (tr.find_all("td")[4].text.strip('\n').splitlines() == []):
                pass
            else:
                item["obtainedFrom"] = tr.find_all("td")[4].text.strip('\n').splitlines()
        if tr.find_all("td")[5].text.strip().replace(",", ""):
            item["price"] = int(tr.find_all(
                "td")[5].text.strip().replace(",", ""))
        items[name] = item
    dump_data(items, "crafting/" + key)
    return items


def scrape_DIYothers(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "roundy"})
    items = {}
    for tr in table[2].find_all("tr")[1:]:
        name = tr.find_all("td")[0].a.text
        item = {
            "name": name,
            "imageLink": tr.find_all("a")[1]['href'],
            "materials": separate_by_br(tr.find_all("td")[2]).lstrip().strip("\n").split(","),
            "materialsImageLink": get_image_links(tr.find_all("td")[2].find_all("img")),
            "sizeImageLink": tr.find_all("td")[3].img.get("data-src"),
            "obtainedFrom": tr.find_all("td")[4].text.strip().strip("\n").splitlines(),
            "price": parse_price(tr.find_all("td")[5].text)
        }
        if (item["obtainedFrom"] == ["Nook Stop (1,000 )"]): # TODO: rewrite this lazy code
            item["obtainedFrom"] = ["Nook Stop (1,000 Nook Miles)"]
        items[name] = item
    dump_data(items, "crafting/" + key)
    return items


def scrape_tops(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "roundy"})
    items = {}
    for tr in table[2].find_all("tr")[2:]:
        name = tr.find_all("td")[0].text.strip()
        item = {
            "name": name,
            # "imageLink": tr.find_all("td")[1].find_all("a")[0]["href"],
            "priceBuy": parse_price(tr.find_all("td")[2].text),
            "priceSell": parse_price(tr.find_all("td")[3].text),
            "source": parse_source(tr.find_all("td")[4]),
            "variations": parse_variations(tr.find_all("td")[5]),
            "variationImageLinks": get_image_links(tr.find_all("td")[5].find_all("img"))
        }
        if tr.find_all("td")[1].find_all("a"):
            item["imageLink"] = tr.find_all("td")[1].find_all("a")[0]["href"]
        items[name] = item
    dump_data(items, "clothing/" + key)
    return items


def scrape_hats(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "roundy"})
    items = {}
    for tableNumber in range(2,10):
        for tr in table[tableNumber].find_all("tr")[2:]:
            name = tr.find_all("td")[0].text.strip()
            item = {
                "name": name,
                # "imageLink": tr.find_all("td")[1].find_all("a")[0]["href"],
                "priceBuy": parse_price(tr.find_all("td")[2].text),
                "priceSell": parse_price(tr.find_all("td")[3].text),
                "source": parse_source(tr.find_all("td")[4]),
                "variations": parse_variations(tr.find_all("td")[5]),
                "variationImageLinks": get_image_links(tr.find_all("td")[5].find_all("img"))
            }
            if tr.find_all("td")[1].find_all("a"):
                item["imageLink"] = tr.find_all("td")[1].find_all("a")[0]["href"]
            items[name] = item
    dump_data(items, "clothing/" + key)
    return items


def scrape_shoes(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "roundy"})
    items = {}
    for tableNumber in range(2,8):
        for tr in table[tableNumber].find_all("tr")[2:]:
            name = tr.find_all("td")[0].text.strip()
            item = {
                "name": name,
                # "imageLink": tr.find_all("td")[1].find_all("a")[0]["href"],
                "priceBuy": parse_price(tr.find_all("td")[2].text),
                "priceSell": parse_price(tr.find_all("td")[3].text),
                "source": parse_source(tr.find_all("td")[4]),
                "variations": parse_variations(tr.find_all("td")[5]),
                "variationImageLinks": get_image_links(tr.find_all("td")[5].find_all("img"))
            }
            if tr.find_all("td")[1].find_all("a"):
                item["imageLink"] = tr.find_all(
                    "td")[1].find_all("a")[0]["href"]
            items[name] = item
    dump_data(items, "clothing/" + key)
    return items


def scrape_umbrellas(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "roundy"})
    items = {}
    for tr in table[2].find_all("tr")[2:]:
        name = tr.find_all("td")[0].text.strip()
        item = {
            "name": name,
            "imageLink": tr.find_all("td")[1].find_all("a")[0]["href"],
            "source": parse_source(tr.find_all("td")[2]),
            "priceBuy": parse_price(tr.find_all("td")[3].text),
            "priceSell": parse_price(tr.find_all("td")[4].text),
        }
        items[name] = item
    dump_data(items, "clothing/" + key)
    return items


def scrape_furniture_housewares(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", {"class": "roundy"})
    items = {}
    for tr in table[3]("tr")[2:]:
        name = tr.find_all("td")[1].text.strip()
        item = {
            "name": name,
            # "imageLink": tr.find_all("td")[1].find_all("a")[0]["href"],
            "priceBuy": parse_price(tr.find_all("td")[2].text),
            "priceSell": parse_price(tr.find_all("td")[3].text),
            "source": parse_source(tr.find_all("td")[4]),
            "variations": parse_variations(tr.find_all("td")[5]),
            "customization": False,
            "sizeLink": tr.find_all("td")[6].img.get("data-src")
        }
        if tr.find_all("td")[1].find_all("a"):
            item["imageLink"] = tr.find_all("td")[0].find_all("a")[0]["href"]
        items[name] = item
    dump_data(items, "furniture/" + key)
    return items


def scrape_flowers(key):
    url = URLS.get(key)
    response = (requests.get(url, timeout=5))
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup("table")

    # availability
    items = {}
    for tr in tables[0]("tr")[2:10]:
        name = tr("td")[0].text.strip()
        t = tables[0]("tr")[2]("td")
        item = {
            "color_image_urls": parse_image_URLs(tr("td")[1]),
            "months": {
                "northern": parse_months([tr("td")[2], tr("td")[3], tr("td")[4], tr("td")[5], tr("td")[6], tr("td")[7], tr("td")[8], tr("td")[9], tr("td")[10], tr("td")[11], tr("td")[12], tr("td")[13]]),
                "southern": parse_months([tr("td")[8], tr("td")[9], tr("td")[10], tr("td")[11], tr("td")[12], tr("td")[13], tr("td")[2], tr("td")[3], tr("td")[4], tr("td")[5], tr("td")[6], tr("td")[7]])
            }
        }
        items[name] = item
    dump_data(items, "flower/availability")

    # genetics_rose
    items = []
    for tr in tables[5]("tr")[2:29]:
        item = {
            "genotype": {
                "red": int(tr("td")[0].text.strip()),
                "yellow": int(tr("td")[1].text.strip()),
                "white": int(tr("td")[2].text.strip())
            },
            "phenotypes_image_url": parse_rose_image_URLs([tr("td")[3].img, tr("td")[4].img, tr("td")[5].img])
        }
        items.append(item)
    dump_data(items, "flower/genetics_rose")
    
    # genetics_others
    items = []
    for tr in tables[6]("tr")[3:30]:
        item = {
            "genotype": {
                "red": int(tr("td")[0].text.strip()),
                "yellow": int(tr("td")[1].text.strip()),
                "white": int(tr("td")[2].text.strip())
            },
            "phenotypes_image_url": {
                "tulips": tr("td")[3].img.get("data-src").replace("/scale-to-width-down/50", ""),
                "pansies": tr("td")[4].img.get("data-src").replace("/scale-to-width-down/50", ""),
                "cosmos": tr("td")[5].img.get("data-src").replace("/scale-to-width-down/50", ""),
                "lilies": tr("td")[6].img.get("data-src").replace("/scale-to-width-down/50", ""),
                "hyacinths": tr("td")[7].img.get("data-src").replace("/scale-to-width-down/50", ""),
                "windflowers": tr("td")[8].img.get("data-src").replace("/scale-to-width-down/50", ""),
                "mums": tr("td")[9].img.get("data-src").replace("/scale-to-width-down/50", "")
            }
        }
        items.append(item)
    dump_data(items, "flower/genetics_others")

    # hybridization_simple
    items = {}
    for table_number in range(7, 15):
        temp = []
        species = tables[table_number]("tr")[0].text.strip()
        for tr in tables[table_number]("tr")[2:8]:
            if len(tr("abbr")) > 0: # some trs do not contain hybridization data
                item = {
                    "parent_a": {
                        "gene": tr("abbr")[0].get("title"),
                        "image_url": tr("abbr")[0]("img")[0].get("data-src").replace("/scale-to-width-down/50", "")
                    },
                    "parent_b": {
                        "gene": tr("abbr")[1].get("title"),
                        "image_url": tr("abbr")[1]("img")[0].get("data-src").replace("/scale-to-width-down/50", "")
                    },
                    "children": parse_hybridization_children(tr("td")[2])
            }
            temp.append(item)
        items[species] = temp
    dump_data(items, "flower/hybridization_simple")

    # hybridization_advanced
    items = {}
    for table_number in range(15, 17):
        temp = []
        species = tables[table_number]("tr")[0].text.strip()
        for tr in tables[table_number]("tr")[2:6]:
            if len(tr("abbr")) > 0:
                item = {
                    "parent_a": {
                        "gene": tr("abbr")[0].get("title"),
                        "image_url": tr("abbr")[0]("img")[0].get("data-src").replace("/scale-to-width-down/50", "")
                    },
                    "parent_b": {
                        "gene": tr("abbr")[1].get("title"),
                        "image_url": tr("abbr")[1]("img")[0].get("data-src").replace("/scale-to-width-down/50", "")
                    },
                    "children": parse_hybridization_children(tr("td")[2])
                }
            temp.append(item)
        items[species] = temp
    dump_data(items, "flower/hybridization_advanced")


if __name__ == "__main__":
    # -- Characters --
    scrape_villagers("villagers")

    # -- Museum --
    # scrape_bugs("bugs")
    # scrape_fish("fish")
    # scrape_fossils("fossils")
    # scrape_artworks("artworks")

    # -- Crafting --
    # scrape_equipments("tools")
    # scrape_equipments("housewares")
    # scrape_equipments("equipments")
    # scrape_equipments("miscellaneous")
    # scrape_equipments("wallMounteds")
    # scrape_DIYothers("others")
    # scrape_wallpapers("wallpaperRugsFloorings")

    # -- Clothing --
    # scrape_tops("tops")
    # scrape_tops("bottoms")
    # scrape_tops("dresses")
    # scrape_hats("hats")
    # scrape_tops("accessories")
    # scrape_tops("socks")
    # scrape_shoes("shoes")
    # scrape_tops("bags")
    # scrape_umbrellas("umbrellas")

    # -- Furniture --
    # scrape_furniture_housewares("furniture_housewares")

    # -- Flower -- 
    # scrape_flowers("flowers")
    pass
