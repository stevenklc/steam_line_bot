import requests
import os 
import json
import time
from bs4 import BeautifulSoup

class Steam_API:
    def __init__(self,region,country):
        self.region = region
        self.country = country
        self.base_url = 'https://api.isthereanydeal.com/'
        self.token_api = os.environ['isthereanydeal_key']
        self.headers = {
            "Connection":"close"
        }

    def search_game(self,game_name,strict):
        url = self.base_url+'v02/search/search/'
        params = {
            'key' : self.token_api,
            'q' : game_name,
            'strict' : strict,
            'limit' : 10
        }

        game_search = requests.get(url,params=params,headers=self.headers)

        return json.loads(game_search.text)


    def steam_cut(self,game_plains):
        # 呼叫API 取得USD最低價
        url = self.base_url+'v01/game/lowest/'
        params = {
            'key' : self.token_api,
            'plains' : game_plains,
            'region' : self.region,
            'country' : self.country,
            'shops':'steam'
        }
        game_price_low = requests.get(url,params=params,headers=self.headers)
        game_price_low = json.loads(game_price_low.text)

        # 取得最低價折扣%數
        game_price_low_cut = game_price_low['data'][game_plains]['cut']

        return game_price_low_cut


    def game_price(self,game_plains):

        params = {
            'key' : self.token_api,
            'plains' : game_plains,
            'region' : self.region,
            'country' : self.country,
            'shops':'steam'
        }        
        
        url = self.base_url+'v01/game/prices/'
        game_url = requests.get(url,headers = self.headers , params=params)
        game_url = json.loads(game_url.text)
        print('--------------------------------')
        print(game_url)
        game_url = game_url['data'][game_plains]['list'][0]['url']
        
        # 取的app id
        app_game = ''
        for i in game_url[-10:]:
            if i.isdigit():
                app_game += i

        url = 'https://store.steampowered.com/app/'+app_game
        buy_url = url
        geame_price_tw = requests.get(url=url,headers=self.headers)
        geame_price_tw = BeautifulSoup(geame_price_tw.text, "html.parser")

        # 取得封面圖片
        gmae_image = geame_price_tw.find('img', class_='game_header_image_full').get('src')

        pack_name = []
        for i in geame_price_tw.find_all('div',class_= 'game_area_purchase_game'):
            for i2 in i.find_all('input',attrs={'name': "subid"}):
                url_value = i2.get('value')
                pack_name.append(url_value)
        
        # 爬取steam_tw頁面取得台幣價格
        game_price_dict_final = {}
        game_price_dict_final['data'] = []
        for packgeids_values in pack_name:
            url = 'https://store.steampowered.com/api/packagedetails/'
            params = {
            'packageids' : packgeids_values,
                'cc' : 'tw'
            }

            steam_price_tw = requests.get(url,params=params,headers=self.headers)
            steam_price_tw = json.loads(steam_price_tw.text)
            game_title = steam_price_tw[packgeids_values]['data']['name']
            game_now_price = (steam_price_tw[packgeids_values]['data']['price']['final'])/100

            search_all = (self.search_game(game_title,1))['data']['results'][0]['plain']
            game_price_low_cut = self.steam_cut(search_all)

            
            game_now_price_cut = steam_price_tw[packgeids_values]['data']['price']['discount_percent']
            game_history_price = round(((steam_price_tw[packgeids_values]['data']['price']['initial'])/100) * ((100 - game_price_low_cut)/100))

            tmp ={
                'title':game_title,
                'now_price':game_now_price,
                'now_cut':game_now_price_cut,
                'history_price':game_history_price,
                'history_cut':game_price_low_cut
                }

            game_price_dict_final['data'].append(tmp)
        
        game_price_dict_final['image'] = gmae_image
        game_price_dict_final['buy_url'] = buy_url

        return game_price_dict_final

if __name__ == "__main__":
    a = Steam_API('us','US')
    c = a.search_game('NBA 2K21','1')
    
    # print(type(a))
    # print(a)
    print('------------------------------------------------------------------------------------------')
    print(c)
    print('------------------------------------------------------------------------------------------')
    search_a = c['data']['results'][0]['plain']
    print(search_a)
    print(type(search_a))

    b = a.game_price(search_a)
    print(b)