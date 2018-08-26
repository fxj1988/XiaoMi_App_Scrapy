import requests
import json
import re
import urllib
import jsonpath
from requests import Request, Session
from queue import *
import threading
import time

url_productView2='https://api.m.mi.com/v1/product/productView2'
url_addCart='https://api.m.mi.com/v1/shopping/addCart'
url_checkout='https://api.m.mi.com/v1/order/checkout'
url_submit='https://api.m.mi.com/v1/order/submit'
url_counter='https://api.m.mi.com/v1/user/counter'
url_bankgo='https://api.m.mi.com/v1/pay/bankgo'
url_category_v2='https://api.m.mi.com/v1/home/category_v2'
url_appInfo='https://api.m.mi.com/v1/home/appInfo'
headers={
    "Host":"api.m.mi.com",
    "Accept":"*/*",
    "Device-Id":"6D148B9046893764B16A5D1E211C6EAC",
    "Mishop-Client-Id":"180100031055",
    "locale":"CN",
    "Mishop-Channel-Id":"",
    #"Mishop-Auth":"08da39804a9245d9;762594697",
    "Network-Carrier":"46001",
    "Accept-Language":"zh-Hans-CN;q=1",
    "Content-Length":"639",
    "User-Agent":"MiShop/4.2.532 (iPhone; iOS 11.4; Scale/3.00)",
    "IOS-App-Version":"4.2.532",
    "Accept-Encoding":"br, gzip, deflate",
    "Connection":"keep-alive",
    "IOS-Version":"system=11.4&device=iPhone9,2",
    "Cookie":"serviceToken=hcVPy0mVe54dOp92UcoT2g2RfqdXL9ZrbWnndtmMyvahv+rXBGw6/z5GUx+zTWQvkFD1HV/0tYeYLEYSxU4TVW6gc9uyaXALTwwxPNHM7BwTWJGTX7uY696C37bqzRLM9VNtO5kMlqdQ7cQjwfnMymWyB4xez5dvr2+xf4mseDg=; xmuuid=XMGUEST-4CE198A0-E89E-4B9A-AFE8-CAC283B09E31",
    "Content-Type":"application/x-www-form-urlencoded",

}

data_addCart_Post = 'addCartPath=%01%0231ioshomecells_auto_fill001022%23t%3Dad%26act%3Dother%26page%3Dhome%26page_id%3D1771%26bid%3D3000122.1%26adp%3D1993%26adm%3D8328%01MSNavBarClearRecommendViewController%23%E6%89%8B%E6%9C%BA%E9%A2%91%E9%81%93-%E6%97%A7%02311800appchannellist_two_type1002008%23t%3Dproduct%26act%3Dother%26page%3Dchannel%26page_id%3D1800%26bid%3D3247689.2%26pid%3D10000110%01MSProductViewControllerios%23bid%3D3191132&app_others=9dOyJmAfMSRLWG%2Bya6b3SV6ouMEWvvqNWOkju5wBBRnVpigLPsqofDXYObBElTnsyF89aTN2oNhWgvkMkae/9CRBCsNVzfBuPqsad/%2BW928pnlgor5lEY0tVuszFgBw0%2BxdLadqS1yzKNKMbdAt8KQ%3D%3D&consumption=1&product_id=2182300107&quick_order=0'
data_category_v2 = 'lat=&lng=&province_name='
data_checkout_first = 'is_ajax=1'
data_checkout_second='address_id=10171109610800560&invoice_version=4&pay_id=1&quick_order=0&shopapi_version=2&support_pay_type=alipaysecurity%2Cmicash_wap%2Cunionpaynative%2Capplepay%2Cantinstal_app%2Cweixin_app%2Cmifinanceinstal_m%2Cbestpay_wap&use_default_coupon=1'
data_submit = 'address_id=10171109610800560&best_time=1&extend_field=%7B%7D&invoice_type=4&pay_id=1&quick_order=0&shipment_id=2&version=v2'
data_counter = ''
data_appInfo = 'lat=39.85662&lng=116.4052&page_id=0&page_index=1&tab_index=0'
data_bankgo = 'bank=alipaysecurity_v11&order_id='

CRAWL_EXIT = False
PARSE_EXIT = False

class APP_ThreadCrawl(threading.Thread):
    def __init__(self,threadName,idQueue,dataQueue,session):
        super(APP_ThreadCrawl, self).__init__()
        self.threadName=threadName
        self.dataQueue=dataQueue
        self.idQueue=idQueue
        self.session=session
        self.headers=headers

    def run(self):
        print("启动 " + self.threadName)
        while not CRAWL_EXIT:
            try:
                commodity_id=self.idQueue.get(False)
                data_commodity_id = 'commodity_id={}&lat=39.85468&lng=116.4037&support_insurance=mi_notebook&support_pay_type=alipaysecurity%2Cmicash_wap%2Cunionpaynative%2Capplepay%2Cantinstal_app%2Cweixin_app%2Cmifinanceinstal_m&version=6'.format(
                    commodity_id)
                response = self.session.post(url_productView2, data=data_commodity_id,headers=headers)
                self.dataQueue.put(response)
            except:
                pass

class APP_ThreadParse(threading.Thread):
    def __init__(self, threadName, dataQueue):
        super(APP_ThreadParse, self).__init__()
        self.threadName = threadName
        self.dataQueue = dataQueue

    def run(self):
        print("启动" + self.threadName)
        while not PARSE_EXIT:
            try:
                response=self.dataQueue.get(False)
                list = jsonpath.jsonpath(response.json(), '$..goods_info')[0]
                list_proInfo = []
                for m in list:
                    dict = {}
                    dict['name'] = m.get('name')
                    dict['price'] = m.get('no_shipment_price')
                    dict['goods_id'] = m.get('goods_id')
                    list_proInfo.append(dict)
                print(list_proInfo)

            except:
                pass
        print("退出" + self.threadName)

def main():
    set_commodityId = set()
    session = Session()
    response = session.post(url_category_v2, data=data_category_v2, headers=headers)
    textView = response.content.decode('utf-8')
    if (textView.find('成功') > 0):
        textView = textView.replace("\\", '')
        re_commodityId = re.findall(r'commodityId":"(.{1,10})",', textView)
        set_commodityId = set(re_commodityId)
    idQueue=Queue()
    for commodityId in set_commodityId:
        idQueue.put(commodityId)

    dataQueue = Queue()
    # 三个采集线程的名字
    crawlList = ["采集线程1号", "采集线程2号", "采集线程3号"]
    # 存储三个采集线程的列表集合
    threadcrawl = []
    for threadName in crawlList:
        thread = APP_ThreadCrawl(threadName, idQueue, dataQueue,session)
        thread.start()
        threadcrawl.append(thread)

    # 三个解析线程的名字
    parseList = ["解析线程1号", "解析线程2号", "解析线程3号"]
    # 存储三个解析线程
    threadparse = []
    for threadName in parseList:
        thread = APP_ThreadParse(threadName, dataQueue)
        thread.start()
        threadparse.append(thread)

    while not idQueue.empty():
        pass
    global CRAWL_EXIT
    CRAWL_EXIT = True

    print("idQueue为空")

    for thread in threadcrawl:
        thread.join()
        print("1")

    while not dataQueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True

    for thread in threadparse:
        thread.join()
        print("2")

    print("谢谢使用！")
if __name__ == "__main__":
    main()
