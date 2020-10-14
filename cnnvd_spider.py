import scrapy


class CnnvdSpider(scrapy.Spider):
    name = "cnnvd"
    start_urls = [
        'http://cnnvd.org.cn/web/vulnerability/querylist.tag?pageno=1&repairLd=',
    ]
    
    def parse_vul_detail(self, response):
        detail_xq_div = response.css(".detail_xq")
        # 1. title
        vul_title = detail_xq_div.css("h2::text").get().strip()
        vul_detail = {
            "漏洞名称":vul_title,
        }
        
        # 2. ul li
        vul_info_list = detail_xq_div.css("ul li")
        for vul_info in vul_info_list:
            vul_info_span = vul_info.css("span::text").get()
            vul_info_a = vul_info.css("a::text").get()
            if vul_info_span is not None:
                vul_info_span = vul_info_span.strip().replace("\xa0", "")
            else:
                vul_info_span = ""
            if vul_info_a is not None:
                vul_info_a = vul_info_a.strip().replace("\xa0", "")
            else:
                vul_info_a = ""
            vul_info_str = vul_info_span + vul_info_a
            if vul_info_str != "":
                vul_info = vul_info_str.split("：")            
                vul_detail[vul_info[0]] = ""
                if len(vul_info) == 2:
                    vul_detail[vul_info[0]] = vul_info[1]
                    
        # 3. d_ldjj
        vul_info_list2 = response.css(".d_ldjj")
        for vul_info in vul_info_list2:
            title = vul_info.css(".title_bt").css("h2::text").get().strip()
            content = ""
            if ("漏洞简介" in title) or ("漏洞公告" in title) or ("参考网址" in title) or ("受影响实体" in title):
                for content_selector in vul_info.css("p::text"):
                    content += content_selector.get().strip()
                # print(content)
            if ("补丁" in title):
                content_selector = vul_info.css("a")
                if len(content_selector) > 0 and content_selector[0] is not None:
                    content = content + "http://cnnvd.org.cn/" + content_selector[0].attrib["href"].strip().replace("javascript:void(0)", "")
                # print(content)
            vul_detail[title] = content
            
        yield vul_detail

    def parse(self, response):
        vul_list = response.css("div.list_list ul li")
        for vul_item in vul_list:
            vul_attr = vul_item.css("a::attr(href)").get()
            yield response.follow(vul_attr, callback=self.parse_vul_detail)

        link_list = response.css(".page")[0].css("a")
        for link in link_list:
            link_text = link.css('a::text').get()
            # print(link_text)
            if "下一页" in link_text:
                next_page = link.css('a')[0].attrib["onclick"].split("'")[1]
                # print(next_page)
                if next_page is not None:
                    yield response.follow(next_page, callback=self.parse)
