import requests
from bs4 import BeautifulSoup
import csv

# 目标网站的URL链接
base_url = "https://ah.huatu.com/zt/zwb/search/"
page_params = "?page={}"

# 创建csv文件并写入表头
with open("job.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["position_code","area","department","position","degree","major","number_of_recruits","number_of_applicants"])
                        #职位代码	地区	部门名称	职位	学历	专业	招考人数	报名人数
    # 遍历前10页数据
    for page in range(1, 179):
        url = base_url + page_params.format(page)
        # 发送GET请求
        response = requests.get(url)

        # 使用BeautifulSoup解析返回的HTML页面
        soup = BeautifulSoup(response.text, "html.parser")

        # 找到所有职位信息所在的表格
        table = soup.find("table")

        # 遍历表格中的所有行并写入csv文件中
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) > 0 and cols[0].text.strip() == "地区":
                continue
            elif len(cols) > 0:
                writer.writerow([cols[0].text.strip(), cols[1].text.strip(), cols[2].text.strip(), cols[3].text.strip(),
                                cols[4].text.strip(), cols[5].text.strip(), cols[6].text.strip(), cols[7].text.strip()])