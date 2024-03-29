# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import urllib.request
import datetime as dt
import pandas as pd
import csv
from insta_explorer.items import InstaExplorerItem


class InstaUrlSpider(scrapy.Spider):
    name = "insta_url"
    allowed_domains = ["instagram.com"]
    start_urls = ["http://instagram.com/"]

    keyword = "댕댕이"
    max_id = ""
    url = ""

    def start_requests(self):

        self.url = (
            "https://www.instagram.com/explore/tags/"
            + self.keyword
            + "/?__a=1&max_id="
            + self.max_id
        )
        print("self.url : " + self.url)
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):

        print("response.url : " + response.url)
        json_data = json.loads(response.body)

        print("json_data : " + str(json_data))
        self.max_id = json_data["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"][
            len(json_data["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]) - 1
        ]["node"]["id"]

        for edge in json_data["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]:

            item = InstaExplorerItem()
            item["max_id"] = self.max_id

            # 본문
            try:
                item["text"] = edge["node"]["edge_media_to_caption"]["edges"][0][
                    "node"
                ]["text"]
            except:
                item["text"] = ""

            # 작성일
            timestamp = edge["node"]["taken_at_timestamp"]
            item["date"] = dt.datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # 좋아요 갯수
            item["like_count"] = edge["node"]["edge_liked_by"]["count"]

            # 비디오?
            if edge["node"]["is_video"]:
                item["explain"] = "Video"
            else:
                item["explain"] = edge["node"]["accessibility_caption"]

            shortcode = edge["node"]["shortcode"]
            item["each_url"] = (
                'https://www.instagram.com/graphql/query/?query_hash=477b65a610463740ccdb83135b2014db&variables={"shortcode":"'
                + shortcode
                + '"}'
            )

            yield item

        # 다음페이지?
        hasNext = json_data["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"][
            "has_next_page"
        ]

        if hasNext is not None:
            self.url = (
                "https://www.instagram.com/explore/tags/"
                + self.keyword
                + "/?__a=1&max_id="
                + self.max_id
            )
            yield response.follow(url=self.url, callback=self.parse)

