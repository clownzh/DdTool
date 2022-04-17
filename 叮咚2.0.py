import time

import uiautomator2 as u2
from threading import Thread
from playsound import playsound

phone = "CUY0219520000007"  #手机的devices


# 连接手机
def connect_phone():
    u2.connect()
    d = u2.connect(phone)
    if not d.service("uiautomator").running():
        # 启动uiautomator服务
        print("start uiautomator")
        d.service("uiautomator").start()
        time.sleep(2)

    if not d.agent_alive:
        print("agent_alive is false")
        u2.connect()
        d = u2.connect(phone)
    return d


class success(Thread):
    def run(self):
        playsound('./1.mp3')

# 时间判断
def is_five_o_clock():
    return time.strftime('%H:%M') >= '05:59'


# 获取当前的时间
def get_current_hour(d):
    info = d.xpath('//*[@resource-id="com.yaya.zone:id/rv_selected_hour"]').get(timeout=1).info
    return info.get("childCount", 0)


# 获取购物车是否有可购买商品
def get_total_price(d):
    return d.xpath('//*[@resource-id="com.yaya.zone:id/tv_sum_money_two"]').exists


# 向下滑动
def swipe_up(d):
    d.swipe(0, 300, 0, 2000)

# 向上滑动
def swipe_down(d):
    d.swipe(0, 1000, 0, 300)

# 排除的商品关键字
exclude_goods = [
    "白酒",
    "盐",
    "抽",
    "长青",
]

# 当前购物车商品
goods = []
# 首页商品数判断
def get_goods_num(d):
    if not d.xpath('//*[@resource-id="com.yaya.zone:id/rl_msg"]').exists:
        return False
    info= d.xpath('//*[@resource-id="com.yaya.zone:id/inner_recycler_view"]').info
    childCount = info.get("childCount", 0)
    count = 0
    if childCount >= 2:
        # 向上滑动
        swipe_down(d)
        info = d.xpath('//*[@resource-id="com.yaya.zone:id/inner_recycler_view"]').info
        childCount1 = info.get("childCount", 0)
        if  childCount*2 == childCount1:
            swipe_down(d)
            info = d.xpath('//*[@resource-id="com.yaya.zone:id/inner_recycler_view"]').info
            childCount = info.get("childCount", 0)

    print("childCount:", childCount)
    for i in range(childCount):
        xpath = '//*[@resource-id="com.yaya.zone:id/inner_recycler_view"]/android.view.ViewGroup[%s]' % str(i + 1)
        exists = d.xpath(xpath).exists
        if exists:
            info = d.xpath(xpath).info
            if info.get("childCount", 0) != 1:
                d.xpath(xpath).click()
                product_info=d.xpath('//*[@resource-id="com.yaya.zone:id/tv_name_new"]').info
                title = product_info.get("text", "")
                index = 0
                for i in exclude_goods:
                    index = title.find(i)
                    if index != -1:
                        break
                if index ==-1:
                    if title not in goods:
                        d.xpath('//*[@resource-id="com.yaya.zone:id/rl_add_cart"]').click()
                        d.xpath('//*[@resource-id="com.yaya.zone:id/iv_back1_head"]').click()
                        goods.append(title)
                    count += 1
                else:
                    d.xpath('//*[@resource-id="com.yaya.zone:id/iv_back1_head"]').click()

    print("首页商品数量：%s" % count)
    print("购物车商品数量:",goods)
    return count >= 1

# 获取当前运力
def get_yun(d):
    if not d.xpath('//*[@resource-id="com.yaya.zone:id/tv_one"]').exists:
        return True
    info=d.xpath('//*[@resource-id="com.yaya.zone:id/tv_one"]').info
    s = "由于近期疫情问题，配送运力紧张，本站点当前运力已约满"
    text = info.get("text", "")
    return text != s



if __name__ == '__main__':
    d = connect_phone()
    count = 1
    count1 = 1
    time_start = time.time()
    while True:
        try:
            d.app_start("com.yaya.zone")
            if  d.xpath('//*[@resource-id="com.yaya.zone:id/iv_back1_head"]').exists:
                d.xpath('//*[@resource-id="com.yaya.zone:id/iv_back1_head"]').click()
            start = time.time()
            yunli = get_yun(d)
            if  get_goods_num(d):
                if yunli:
                    print("上货了，运力充足")
                    success().start()
                    d.xpath('//*[@resource-id="com.yaya.zone:id/tv_tab_car"]').click()
                    if d(textContains="去结算(").exists:
                        print("点击结算")
                        d(textContains="去结算(").click()

                    if d(text="立即支付").exists:
                        print("点击立即支付")
                        d(text="立即支付").click()
                else:
                    print("上货了，运力不足")
                    time.sleep(1)
                    swipe_up(d)
                    swipe_up(d)
                    print("首页查询本次花费时间:", time.time() - start)
                    print("首页查询总共花费时间:", (time.time() - time_start) / 60, "分钟，第", count1, "次")
                    count1 += 1
            else:
                if not get_total_price(d):
                    swipe_up(d)
                    time.sleep(1)
                    print("购物车查询本次花费时间:", time.time() - start)
                    print("购物车查询总共花费时间:", (time.time() - time_start) / 60, "分钟，第", count1, "次")
                    count1 += 1
                    continue
                if d(textContains="去结算(").exists:
                    print("点击结算")
                    d(textContains="去结算(").click()

                if d(text="我知道了").exists:
                    print("点击我知道了")
                    d(text="我知道了").click()
                if d(text="重新加载").exists:
                    print("点击重新加载")
                    d(text="重新加载").click()

                if d(text="立即支付").exists:
                    print("点击立即支付")
                    d(text="立即支付").click()

                if d(text="下单失败").exists:
                    print("下单失败")
                    if d(text="返回购物车").exists:
                        print("点击返回购物车")
                        d(text="返回购物车").click()
                d.xpath('//*[@resource-id="com.yaya.zone:id/sw_pay_left"]').click_exists(timeout=1)
                hour_count = get_current_hour(d)
                for i in range(hour_count):
                    info = d.xpath(
                        '//*[@resource-id="com.yaya.zone:id/rv_selected_hour"]'
                        '/android.view.ViewGroup[%s]' % str(i + 1)).get(timeout=1).info
                    if info.get("enabled", "") != "false":
                        print("TMD 有运力了")
                        d.xpath(
                            '//*[@resource-id="com.yaya.zone:id/rv_selected_hour"]'
                            '/android.view.ViewGroup[%s]' % str(i + 1)).click_exists(timeout=1)
                        print("点击了第" + str(i + 1) + "个")
                        success().start()
                        if d(text="立即支付").exists:
                            print("点击立即支付")
                            d(text="立即支付").click()

                        if d(text="下单失败").exists:
                            print("下单失败")
                            if d(text="返回购物车").exists:
                                print("点击返回购物车")
                                d(text="返回购物车").click()
                    if i == hour_count - 1:
                        print("没有运力了")
                        d.xpath('//*[@resource-id="com.yaya.zone:id/'
                                'iv_dialog_select_time_close"]').click_exists(timeout=1)
                        d.xpath('//*[@resource-id="com.yaya.zone:id/'
                                'iv_order_back"]').click_exists(timeout=1)

                if d(text="确认交易").exists:
                    print("点击确认交易")
                    d(text="确认交易").click()
                    success().start()

                if d(text="确认并支付").exists:
                    print("点击确认并支付")
                    d(text="确认并支付").click()

                if d(resourceId="btn-line").exists:
                    print("确认支付")
                    d(resourceId="btn-line").click()
                    success().start()

                print("本次花费时间:", time.time() - start)
                print("总共花费时间:", (time.time() - time_start) / 60, "分钟，第", count, "次")
                count += 1


        except Exception as e:
            pass
