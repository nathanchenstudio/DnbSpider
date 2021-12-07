# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import motor.motor_asyncio


class MongoDBPipeline:
    def open_spider(self, spider):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(spider.settings.get('MONGODB_URI'))
        self.collection = self.client[spider.settings.get('MONGODB_DATABASE')][
            spider.settings.get('MONGODB_COLLECTION')]

    def close_spider(self, spider):
        self.client.close()

    async def process_item(self, item, spider):
        await self.collection.update_one({'url': item['url']},
                                         {'$set': item},
                                         upsert=True)
        return item
