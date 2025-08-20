import asyncio
import typing

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import async_playwright
from botpy import logging

_log = logging.get_logger()

class HltvScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    #页面加载优化，不加载图片字体样式资源
    async def block_images_and_fonts(self):
        async def route_intercept(route, request):
            if request.resource_type in ["font"]:
                await route.abort()
            else:
                await route.continue_()

        await self.page.route("**/*", route_intercept)
    async def accept_cookies(self):
        try:
            await self.page.wait_for_selector("#CybotCookiebotDialogBodyButtonDecline", timeout=10000)
            await self.page.click("#CybotCookiebotDialogBodyButtonDecline")
            _log.info("已接受 cookies协议")
        except Exception as e:
            _log.error(e)
    async def start(self):
        _log.info("开始启动页面")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.block_images_and_fonts()
        #首次到首页，并接受cookie
        # await self.page.goto("https://www.hltv.org/", timeout=60000, wait_until="load")
        _log.info("正在首页")
        # await self.accept_cookies()
        # try:
        #     await self.page.wait_for_selector("#CybotCookiebotDialogBodyButtonDecline", timeout=5000)
        #     await self.page.click("#CybotCookiebotDialogBodyButtonDecline")
        #     _log.info("已接受 cookies协议")
        #
        #     # 保存 cookie
        #     cookies = await self.context.cookies()
        #     _log.info(cookies)
        #     # 后续再新建 context 或 page 时
        #     set_cookies = []
        #     for c in cookies:
        #         set_cookies.append(SetCookieParam(
        #             name=c["name"],
        #             value=c["value"],
        #             domain=c.get("domain"),
        #             path=c.get("path", "/"),
        #             secure=c.get("secure", False),
        #             httpOnly=c.get("httpOnly", False),
        #             sameSite=c.get("sameSite", None),
        #             expires=c.get("expires", -1)
        #         ))
        #     await self.context.add_cookies(set_cookies)
        # except:
        #     _log.info("Cookie 弹窗不存在")

    async def scrap_news_list(self):
        await self.start()
        await self.page.goto("https://www.hltv.org/", timeout=60000, wait_until="load")
        await self.accept_cookies()
        news_today = []
        #有可能有热点新闻占据第一个 standardlist
        newsgrouping = self.page.locator("div.newsgrouping")
        living_name = None
        coantainer_list = []
        if await newsgrouping.count()!=0:
            # 如果有比赛在播，则前两个container
            all = await self.page.locator("div.standard-box.standard-list").all()
            for i in range(2):
                coantainer_list.append(all[i])
            living_name = await newsgrouping.locator(":scope div.newsgrouping-header").inner_text()
        else:
            #没有比赛，则第一个container
            f = self.page.locator("div.standard-box.standard-list").first
            coantainer_list.append(f)
        for container in coantainer_list:
            await container.wait_for(state="visible", timeout=20000)
            links = container.locator("a")
            count = await links.count()

            for i in range(count):
                newstext = links.nth(i).locator("div.newstext")
                if await newstext.count()==0:
                    #没有newstext，则为头条，只给标题
                    newstext = links.nth(i).locator("div.featured-newstext")
                    title = await newstext.inner_text()
                    news_today.append({"title": title, "recent": None})
                    continue
                title = await newstext.inner_text()

                recent = await links.nth(i).locator("div.newstc div.newsrecent").inner_text()
                news_today.append({"title": title, "recent": recent})
                _log.info(newstext)
        await self.browser.close()
        return living_name,news_today

    async def scrap_match_list(self):
        await self.start()
        await self.page.goto("https://www.hltv.org/", timeout=60000, wait_until="load")
        container = self.page.locator("div.top-border-hide")
        await container.wait_for()
        links = container.locator("> a")
        _log.info(links)
        count = await links.count()
        matches_today = []
        for i in range(count):
            teamrow = await links.nth(i).locator(":scope div.teamrow").all()
            #队名 team1 team2
            names = [await t.locator(":scope span").inner_text() for t in teamrow]
            #比分 div
            twoRowExtra = await links.nth(i).locator(":scope div.livescore.twoRowExtraRow").all()
            _log.info(names)
            _log.info(twoRowExtra)
            if not names:
                continue
            if not twoRowExtra:
                #比赛未开始
                time = await links.nth(i).locator(":scope div.middleExtra").inner_text()
                matches_today.append({
                    "team1": {"name": names[0], "score": 0, "mapsWon": 0,"time":time},
                    "team2": {"name": names[1], "score": 0, "mapsWon": 0,"time":time}
                })
            else:
                #比赛一开始
                scores = []
                for extra in twoRowExtra:
                    #此处用data属性定位
                    score = await extra.locator(":scope span[data-livescore-current-map-score]").inner_text()
                    #嵌套了一个span
                    mapsWon = await extra.locator(":scope span.spacing >> span").inner_text()
                    scores.append([score, mapsWon])
                matches_today.append({
                    "team1": {"name": names[0], "score": scores[0][0], "mapsWon": scores[0][1],"time":None},
                    "team2": {"name": names[1], "score": scores[1][0], "mapsWon": scores[1][1],"time":None}
                })
        await self.browser.close()
        return matches_today

    async def stop(self):
        await self.browser.close()
        await self.playwright.stop()

# 使用示例
async def main():
    scraper = HltvScraper()
    await scraper.start()
    news = await scraper.scrap_news_list()
    # matches = await scraper.scrap_match_list()
    print(news)
    # print(matches)
    await scraper.stop()

if __name__ == "__main__":
    scraper = HltvScraper()
    scraper.start()
    news = scraper.scrap_news_list()
    print(news)
