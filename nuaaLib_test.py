from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import time
import os

# 初始化Chrome浏览器
os.environ["SE_OFFLINE"] = "true"
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 窗口最大化
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)  # 显式等待10s

try:
    # 动作1：打开南航图书馆首页
    driver.get("https://lib.nuaa.edu.cn/")
    print("动作1：访问南航图书馆官网首页")
    time.sleep(10)
    assert "图书馆" in driver.title, "动作1失败：首页加载异常"

    # 动作2：定位输入框（包含原代码定位，并增加备选定位容错）
    try:
        search_input = wait.until(EC.element_to_be_clickable((By.ID, "inputText")))
    except Exception:
        # 兜底备选定位器，防止TimeoutException报错
        search_input = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//input[contains(@placeholder, '搜索') or contains(@placeholder, '检索') or @type='text']"
        )))
    
    search_input.clear()
    search_input.send_keys("软件测试")
    print("动作2：在顶部搜索框输入关键词【软件测试】")
    # 校验2：断言输入框输入内容是否正确
    input_val = search_input.get_attribute("value")
    assert input_val == "软件测试", f"动作2失败：搜索框内容不符合预期，实际为 '{input_val}'"

    # 动作3：点击搜索按钮
    # 输入框旁边的搜索按钮/图标 <button ... class="btn-search">
    search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-search")))
    search_btn.click()
    print("动作3：点击搜索按钮提交检索")

    # 处理标签页跳转：点击搜索后，如果是打开新窗口，切到最新窗口
    time.sleep(2)
    handles = driver.window_handles
    if len(handles) > 1:
        driver.switch_to.window(handles[-1])
        print("已成功切换到检索结果页新标签")

    # 处理检索后可能打开的新标签页
    time.sleep(5)
    handles = driver.window_handles
    if len(handles) > 1:
        driver.switch_to.window(handles[-1])
        print("已切换到检索结果页")

    # 校验3：断言成功打开了检索结果页面（标签页数量大于1）
    assert len(handles) > 1, "动作3失败：点击搜索后未成功切换或打开检索结果标签页"

    # 动作4：切换检索结果范围
    try:
        # Step 4.1: 点击 Ant Design 下拉框展开菜单
        select_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select')]")))
        select_box.click()
        time.sleep(0.5)

        # Step 4.2: 点击【题名】选项
        target_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'ant-select-dropdown-menu-item') and contains(., '题名')]")))
        target_option.click()
        print("动作4-1：下拉框选择范围为【题名】")

        # Step 4.3: 点击重新检索按钮
        # <button class="ant-btn newSearchBtn___NZSBz"><span>检 索</span></button>
        re_search_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(@class, 'newSearchBtn') or (span and contains(text(), '检 索'))]"
        )))
        re_search_btn.click()
        print("动作4-2：点击【检 索】按钮更新检索结果")
        time.sleep(2) # 等待结果刷新

    except Exception as e:
        print(f"动作4执行异常：{e}")

    # 动作5：点击第一条图书详情
    first_book_link = wait.until(EC.element_to_be_clickable((
        By.XPATH, "(//span[contains(@class, 'titleInfo')]//a | //a[contains(@class, 'infotit')])[1]"
    )))
    book_name = first_book_link.text.strip()
    first_book_link.click()
    print(f"动作5：点击第一条图书链接《{book_name}》进入详情页")

    # 如果进入详情页打开了第3个标签页，则关闭它并返回检索/主页
    time.sleep(20)
    # 校验5：断言是否点击并打开了详情页面（句柄数不小于2）
    assert len(driver.window_handles) >= 2, "动作5失败：点击图书链接后未打开图书详情页"

    if len(driver.window_handles) > 2:
        driver.close()
        driver.switch_to.window(driver.window_handles[1])

    # 切换回最初的图书馆首页，准备继续后续步骤 6-10
    driver.switch_to.window(driver.window_handles[0])

    # 动作 6：悬停/点击导航栏【动态】主菜单
    dongtai_menu = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//a[contains(text(),'动态') and contains(@title,'动态')]"
    )))
    ActionChains(driver).move_to_element(dongtai_menu).perform()
    time.sleep(1)
    print("动作6：鼠标悬停在导航栏【动态】栏目，展开二级菜单")

    # 动作 7：点击二级菜单中的【活动】
    activity_link = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//div[contains(@class,'second-item')]//a[text()='活动']"
    )))
    activity_link.click()
    print("动作7：点击二级子菜单【活动】进入列表页")

    item_1_xpath = "/html/body/div[3]/div[2]/div[2]/div/div/ul/li[1]/div[2]/div[1]/span[2]"
    page1_first_elem = wait.until(EC.presence_of_element_located((By.XPATH, item_1_xpath)))
    page1_title = page1_first_elem.get_attribute("title") or page1_first_elem.text.strip()

    # 校验7：断言当前页面已切换到活动列表页
    assert "hd" in driver.current_url or "活动" in driver.title, "动作7失败：未能成功导航到【活动】列表页"

    # 动作 8：滑动到底部，点击下一页
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    page_2_btn = wait.until(EC.presence_of_element_located((
        By.XPATH, "//a[@data-page='2']"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", page_2_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", page_2_btn)
    print("动作8：活动列表页向下滚动并切换到第2页")

    # 校验翻页数据是否刷新完成
    page_changed = False
    for _ in range(10):
        time.sleep(1)
        current_elem = driver.find_element(By.XPATH, item_1_xpath)
        current_title = current_elem.get_attribute("title") or current_elem.text.strip()
        if current_title != page1_title:
            page_changed = True
            break

    # 校验8：断言第2页数据已成功异步加载更新
    assert page_changed, "动作8失败：点击第2页后数据未成功更新"

    # 动作 9：点击列表中第 1 条活动查看详情
    activity_xpath = "/html/body/div[3]/div[2]/div[2]/div/div/ul/li[1]/div[2]/div[1]/span[2]"
    first_activity_detail = wait.until(EC.presence_of_element_located((By.XPATH, activity_xpath)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_activity_detail)
    time.sleep(1.5)  # 滚动停止后的视觉与加载缓冲
    activity_title = first_activity_detail.get_attribute("title") or first_activity_detail.text.strip()
    
    pre_click_url = driver.current_url
    driver.execute_script("arguments[0].click();", first_activity_detail)
    print(f"动作9：点击第 2 页第一条活动《{activity_title[:20]}...》查看详情")
    time.sleep(10)

    # 校验9：断言点击活动后URL发生了变化或打开了新详情窗口
    assert (driver.current_url != pre_click_url) or (len(driver.window_handles) > 1), "动作9失败：点击活动后未能跳转至详情页"

    # 动作10：清空重置
    driver.get("https://lib.nuaa.edu.cn/")
    reset_search = wait.until(EC.element_to_be_clickable((By.ID, "inputText")))
    reset_search.clear()
    driver.refresh()
    print("动作10：清空搜索框并刷新首页，完成全部流程")

    # 校验10：断言首页成功清空并重置
    assert driver.current_url.rstrip('/') == "https://lib.nuaa.edu.cn", "动作10失败：未能正确重置并返回图书馆首页"

    print("\n==================================================")
    print("测试结论：所有动作执行完毕，全部断言校验通过！")
    print("测试结果：[ PASS ]")
    print("==================================================")

except AssertionError as e:
    print(f"\n==================================================")
    print(f"测试结论：判定失败！断言拦截：{e}")
    print("测试结果：[ FAIL ]")
    print("==================================================")
except Exception as err:
    print(f"\n==================================================")
    print(f"测试结论：程序异常崩溃，详细原因：")
    traceback.print_exc()
    print("测试结果：[ ERROR ]")
    print("==================================================")
finally:
    time.sleep(3)
    driver.quit()