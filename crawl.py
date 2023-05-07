import requests  # 网络请求模块
import json  # json数据解析模块
import re  # 正则表达式模块

rankings_list = []  # 保存排行数据的列表


class Crawl(object):
    # 获取排行
    def get_rankings(self, url):
        # 创建头部信息
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/109.0.0.0 Safari/537.36"}
        # 网页的页数
        page = 1
        # 初始索引
        index = 0
        while True:
            if page == 6:
                break
            response = requests.get(url.format(page=page), headers=headers)  # 发送网络请求，获取服务器响应
            book_str = response.text.split('(', 1)[1].rsplit(')', 1)[0]  # 提取func()里面的信息
            book_dic = eval(book_str)  # 把字符串信息转换为字典信息
            book_list = book_dic['data']['books']  # 获取图书所有信息
            for li in book_list:
                # 商品索引
                index = index + 1
                # 获取图书id
                jd_id = li['bookId']
                # 获取图书名称
                book_name = li['bookName']
                # 获取图书出版社
                press = li['publisher']
                # 获取图书详情页地址
                item_url = 'https://item.jd.com/' + str(jd_id) + '.html'  # 组建完整的详情页地址
                # 京东价格
                jd_price = li['sellPrice']
                # 定价
                ding_price = li['definePrice']
                # 将所有数据添加到列表中
                rankings_list.append((index, book_name, jd_price, ding_price, press, item_url, jd_id))
            page += 1

    # 获取评价内容,score参数差评为1、中评为2、好评为3，0为全部
    def get_evaluation(self, score, id):
        # 好评率
        self.good_rate_show = None
        # 评价请求地址参数，callback为对应书名json的id，
        # productId书名对应的京东id
        # score评价等级参数差评为1、中评为2、好评为3，0为全部
        # sortType类型，6为时间排序，5为推荐排序
        # pageSize每页显示评价10条
        # page页数
        params = {
            'callback': 'fetchJSON_comment98',
            'productId': id,
            'score': score,
            'sortType': 6,
            'page': 0,
            'pageSize': 10,
            'isShadowSku': 0,
            'fold': 1,
        }
        # 评价请求地址
        url = 'https://club.jd.com/comment/skuProductPageComments.action'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/109.0.0.0 Safari/537.36',
            'Referer': 'https://item.jd.com/'}
        # 发送请求
        evaluation_response = requests.get(url, params=params, headers=headers)
        if evaluation_response.status_code == 200:
            evaluation_response = evaluation_response.text
            try:
                # 去除json外层的括号与名称
                t = re.search(r'({.*})', evaluation_response).group(0)
            except Exception as e:
                print('评价的json数据匹配异常！')
            j = json.loads(t)  # 加载json数据
            commentSummary = j['comments']
            if self.good_rate_show == None:
                self.good_rate_show = j['productCommentSummary']['goodRateShow']
            for comment in commentSummary:
                # 评价内容
                c_contetn = comment['content']
                # 时间
                c_time = comment['creationTime']
                # 京东昵称
                c_name = comment['nickname']
                # 通过哪种平台购买
                c_client = comment['userClient']
                # 会员级别
                # c_userLevelName = comment['userLevelName']
                # 好评差评 1差评 2-3 中评 4-5好评
                c_score = comment['score']
                # print(
                #     '\n{} {} {}  {}\n{}\n'.format(c_name, c_time, str(c_score) + '颗星', c_client,
                #                                      c_contetn))
            # 判断没有指定的评价内容时
            if len(commentSummary) == 0:
                # 返回好评率与无
                return self.good_rate_show, '无'
            else:
                # 根据不同需求返回不同数据，这里仅返回好评率与最新的评价时间
                return self.good_rate_show, commentSummary[0]['creationTime']


# c = Crawl()
# # c.get_rankings('https://gw-e.jd.com/client.action?callback=func&body={{"moduleType":1,"page":{page},"pageSize":20,'
# #                '"scopeType":1,"month":0}}&functionId=bookRank&client=e.jd.com&_=')
# c.get_rankings('https://gw-e.jd.com/client.action?callback=func&body={{"moduleType":1,"page":{page},"pageSize":20,'
#                '"scopeType":1,"month":0,'
#                '"categoryFirst":"计算机与互联网"}}&functionId=bookRank&client=e.jd.com&_=')
# c.get_evaluation(1, '11993134')

