#引入selenium库中的 webdriver 模块
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
import sys

options = Options()
#取消控制台报警
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#打开谷歌浏览器
s = Service(executable_path='./browser_driver/chromedriver.exe')
driver = webdriver.Chrome(service=s,options=options)


"""
切换页面时会产生竞争条件,会导致无法切换的情况,一种解决方法是加上time.sleep(2),另一种就是隐性等待。

web.implicitly_wait()，隐性等待设置了一个时间，在一段时间内网页是否加载完成，如果完成了，
就进行下一步；在设置的时间内没有加载完成，则会报超时加载。

缺点是不智能s,因为随着ajax技术的广泛应用,页面的元素往往都可以时间局部加载，也就是在整个页面没有加载完的时候，
可能我们需要的元素已经加载完成了，那就么有必要再等待整个页面的加载，执行进行下一步，而隐性等待满足不了这一点；

另外一点，隐性等待的设置时全局性的，在开头设置过之后，整个的程序运行过程中都会有效，都会等待页面加载完成；不需要每次设置一遍；
"""
driver.implicitly_wait(10)#隐式等待20s


#登录主页
web_path='https://passport2.chaoxing.com/login?newversion=true&refer=http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Flist%3FdeptIdEnc%3D214d62ddb0e920e7'
driver.get(web_path)



#输入账号和密码并登录
driver.find_element(By.XPATH,'//*[@id="phone"]').send_keys('17853265996')#账号
driver.find_element(By.XPATH,'//*[@id="pwd"]').send_keys('123456zfc')#密码
driver.find_element(By.XPATH,'//*[@id="loginBtn"]').click()#登录


today=False #隔天
# today=True #当天
if today:
    #切换页面后默认是当天，然后进入七楼自习室选座
    driver.find_element(By.XPATH,'/html/body/div/ul[1]/li[7]/span').click()
else:
    #切换到隔天页面
    driver.find_element(By.XPATH,'//*[@id="scr_time"]/ul/li[2]').click()
    #进入七楼自习室选座
    driver.find_element(By.XPATH,'/html/body/div/ul[1]/li[7]/span').click()


have_seat=False#用来判断是否选中空座


#筛选座位
def choice_seat():
    global have_seat#声明使用全局变量


    #选择开始和结束时间，并确定
    """
    直接选择最大的开始和结束时间,id:1-27
    对于每个元素,其class类型表示该时间是否可选
    time_cell noSelect:表示不可选
    time_cell:表示可选
    """
    first_id=1 #开始时间
    for id in range(1,27):
        element=driver.find_element(By.XPATH,'/html/body/div/div[6]/ul/li[%s]'%(id))
        id_class=element.get_attribute("class")#get_attribute获取元素的指定属性
        if id_class=="time_cell":
            first_id=id #确定开始时间
            break
    driver.find_element(By.XPATH,'/html/body/div/div[6]/ul/li[%s]'%(first_id)).click()#选中开始时间
    
    #12:00-12:30=9     17:00-17:30=19    21:00-21:30=27
    driver.find_element(By.XPATH,'/html/body/div/div[6]/ul/li[27]').click()#选中结束时间，这里
    driver.find_element(By.XPATH,'/html/body/div/div[6]/div[1]/span[3]').click()#确定


    #切换到选座界面时，由于是动态页面所以容易出现局部加载，进而导致后面的操作因为冲突而出错
    #等待ajax完成调用，等待10秒,没0.5秒尝试一次，10秒后还没加载成功将报错！
    #注意下面的代码有时候也会出错，因为有时候因为网络等原因，会把局部加载固定，此时ajax也已完成调用
    WebDriverWait(driver,10,0.1).until(lambda s: s.execute_script("return jQuery.active == 0"))


    """
    注意每个座位的class属性决定着这个座位能不能被选
    grid_cell grid_lock:无法选中
    grid_cell grid_seat:可以选中
    """
    #筛选578-601的座位
    id_list=np.arange(579,602,2)
    np.random.set_state(np.random.get_state())#设置随机数,不然每次的随机数种子都一样.
    np.random.shuffle(id_list)#随机打乱
    for id in id_list:
        #通过xpath获取id对应的元素
        element=driver.find_element(By.XPATH,'//*[@id="content-container"]/div[%s]'%(id))
        id_class=element.get_attribute("class")#get_attribute获取元素的指定属性
        #显示可选
        if id_class=='grid_cell grid_seat':
            element.click()#选中座位
            driver.find_element(By.XPATH,'/html/body/div/div[4]/p').click()#提交选中的座位
            have_seat=True
            print('选中!',id)
            break


    #如果上面的座位没选中,接着筛选268-290的座位
    if not have_seat:
        id_list=np.arange(269,290,2)
        np.random.set_state(np.random.get_state())#设置随机数,不然每次的随机数种子都一样.
        np.random.shuffle(id_list)#随机打乱
        for id in id_list:
            #通过xpath获取id对应的元素
            element=driver.find_element(By.XPATH,'//*[@id="content-container"]/div[%s]'%(id))
            id_class=element.get_attribute("class")#get_attribute获取元素的指定属性
            if id_class=='grid_cell grid_seat':
                element.click()#选中座位
                driver.find_element(By.XPATH,'/html/body/div/div[4]/p').click()#提交选中的座位
                have_seat=True
                print('选中!',id)
                break


#多次循环选座,这样可以定时选座,或没选中时盯着这几个座来选.
for i in range(10):
    choice_seat()#开始选座
    if have_seat:#如果选中就提交
        break
    else:#没有选中等待一秒,刷新页面,重新选
        print("刷新 重选!")
        driver.refresh()#刷新当前页面

time.sleep(2)
driver.quit()
s.stop()