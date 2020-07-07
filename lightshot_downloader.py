import bs4
import random
import string
import cfscrape
import requests
import tkinter as tk

def draw_window():
    """
    Lightshot downloader by Ferloerer

    © Ferloerer 2020

    """
    UI_window = tk.Tk()
    UI_window.geometry("300x300")
    UI_window.title("Lightshot-Downloader")


    ##vars for everything
    vpnHopEnabled = tk.IntVar()

    # labels and inputs
    Amount_Label = tk.Label(UI_window, text="Number of images:")
    Amount_input = tk.Entry(UI_window)

    vpn_hop = tk.Checkbutton(UI_window, text="Activate VPN-HOP ", variable=vpnHopEnabled)


    def start_download():
        Downloader(limit=int(Amount_input.get()), proxy=vpnHopEnabled.get())
        print("Download started")
        UI_window.destroy()


    # buttons
    Start_button = tk.Button(UI_window, text="Start download", command=start_download)
    Amount_Label.pack()
    Amount_input.pack()
    Start_button.pack(anchor="s", pady=15)
    vpn_hop.pack(anchor="s", pady=15)


    # finish everything and start mainloop
    UI_window.mainloop()


class Downloader:
    def __init__(self, limit, proxy=True):
        # init variables
        self.base_url = "https://prnt.sc/"
        self.limit = limit
        self.proxy = proxy

        # Proxy setup
        if proxy:
            self.proxy_list = ["https://" + x for x in open("http_proxies.txt").readlines()]
            self.current_proxy = {
                "https": "",
            }
            self.proxy_index = 1

        # lists for available chars and numbers for link generation
        self.key_list = list(string.ascii_lowercase)
        self.number_list = [x for x in range(0, 10)]

        # setup mainloop for download
        self.iterations = 0
        while self.iterations < self.limit:
            self.request_pic()
            self.store_images()

            self.iterations += 1

    def generate_url(self):
        random_chars = []
        random_numbs = []

        def random_abc(amount, element, choice, abc=False):
            for x in range(0, amount):
                rand_int = random.randint(0, len(choice)-1)
                if abc:
                    element.append(choice[rand_int])
                else:
                    element.append(rand_int)

        random_abc(3, random_chars, self.key_list, abc=True)
        random_abc(3, random_numbs, self.number_list)

        random_chars = "".join(random_chars)
        random_numbs = "".join(map(str, random_numbs))

        return self.base_url + random_numbs + random_chars

    def request_pic(self):
        try:
            # change current proxy to ip of proxy list via self.proxy_index
            # self.proxy_index will be changed if response code of request is 403 aka request denied :)
            # when self.proxy_index is increased, proxy will be automatically changed

            self.scraper_object = cfscrape.create_scraper()

            if self.proxy:
                self.current_proxy["https"] = self.proxy_list[self.proxy_index]
                req = self.scraper_object.get(self.base_url + self.generate_url(), proxies=self.current_proxy)

            else:
                req = self.scraper_object.get(self.base_url + self.generate_url())

            if req.status_code == 403:
                self.proxy_index += 1
                raise Exception("Proxy banned: " + req.status_code)
            soup = bs4.BeautifulSoup(req.content, "html.parser")
            img_element = soup.find("img", class_="screenshot-image").attrs
            self.img = img_element["src"]
        except Exception as E:
            print("Proxy not available.. Skipping")
            if "Max retries " in str(E):
                self.proxy_index += 1
            self.img = None
        return self.img

    def store_images(self):
        # store image
        try:
            print(self.img)
            if self.proxy:
                res = requests.get(self.img, proxies=self.current_proxy)
            else:
                res = requests.get(self.img)
            if res.status_code == 403:
                self.proxy_index += 1
                raise Exception("Proxy banned")
            img = open("img{}.png".format(str(self.iterations + 1)), "wb")
            img.write(res.content)
            img.close()
        except Exception as e:
            if "Max retries " in str(e):
                self.proxy_index += 1
            if "Invalid URL" in str(e):
                self.iterations -= 1
            print("Proxy not available or generated URL not existent --> Skipping")
            pass


print(draw_window.__doc__)
draw_window()