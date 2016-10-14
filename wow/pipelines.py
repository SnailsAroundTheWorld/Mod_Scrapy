# -*- coding: utf-8 -*-

# Study by jackgitgz/CnblogsSpider

from twisted.enterprise import adbapi
from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors
import time


class MySQLStorePipeline(object):
    global dbtable

    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.auto_db_list = dbtable['auto_list']
        self.auto_db_content = dbtable['auto_content']

    @classmethod
    def from_settings(cls, settings):
        global dbtable
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbtable = dict(
            auto_list=settings['MYSQL_AUTO_LIST'],
            auto_content=settings['MYSQL_AUTO_CONTENT'],
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def _Ceshi(self, conn, item, spider):
        print " >>>>>>"
        print item['link']
        if  item['link'] == "u'javascript:void(0);'":
            print "||||||"
            pass

    def process_item(self, item, spider):
        # time.sleep(2)
        # 这里写存入 List 表的逻辑
        if spider.name == 'AutoHomeList':
            query = self.dbpool.runInteraction(
                self._List_do_save, item, spider)
            query.addErrback(self._handle_error, item, spider)
            query.addBoth(lambda _: item)
            return query
        # return item

    # List 表业务逻辑
    def _List_do_save(self, conn, item, spider):
        item['title'] = ''.join(item['title'])
        item['link'] = ''.join(item['link'])
        linkmd5id = self._get_md5(item['link'])
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        conn.execute("select 1 from `%s` where linkmd5id = '%s'" %
                     (self.auto_db_list, linkmd5id))
        ret = conn.fetchone()
        if ret:
            print '>>> 链接已存在：%s' % (item['link'].encode("utf-8"))
            # sql = "update `%s` set  link = '%s', updated_at = '%s' where linkmd5id = '%s'" % (
            #     self.auto_db_list,  item['link'], now, linkmd5id)
            # # print sql
            # conn.execute(sql)
            # print '>>>>> UPDATE SUCCESS'
            # conn.commit()
        else:
            sql = "insert into `%s` (linkmd5id, title, link, created_at) values('%s', '%s', '%s', '%s')" % (
                self.auto_db_list, linkmd5id, item['title'], item['link'], now)
            conn.execute(sql)
            print '>>> 链接已添加：%s' % (item['link'].encode("utf-8"))
            # conn.commit()
        return True


    # 获取url的md5编码，
    def _get_md5(self, item):
        return md5(item).hexdigest()

    # 异常处理
    def _handle_error(self, failure, item, spider):
        print failure
        log.err(failure)
