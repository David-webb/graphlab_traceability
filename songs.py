#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on March 31, 2016

@author: maobo

producer, consumer and transporter simulation

模拟生产者，消费者与运输者，并输出相关记录，用于溯源分析

'''

#coding=cp936
from random import randint
from time import sleep
from Queue import Queue
import threading
import datetime
import settings

class Producer(threading.Thread):
    def __init__(self, name="", qn=20, inn=1, outn=1, t=1.0, loop=10):
        threading.Thread.__init__(self)
        self.name = name
        self.sin = Queue(qn)
        self.sout = Queue(qn)
        self.inn = inn
        self.outn = outn
        self.t = t
        self.f = open(name, 'w')        #
        self.loop = loop
        self.startime = settings.STARTIME
        self.timeRate = settings.TIMERATE

    def getPQueue(self):        # producer 的输出队列
        return self.sout

    def getInOueue(self):       # producer 的输入队列
        return self.sin

    def getTime(self):
        now = datetime.datetime.now()
        delta = (now - self.startime).seconds * self.timeRate
        tmp = self.startime + datetime.timedelta(seconds=delta)
        return tmp.strftime("%Y-%m-%d %H:%M:%S")
        pass

    """
    *************生产操作****************
    功能：
        完成产品生产，其过程分为：
        １.原料数量判断，不够则等１秒，然后退出该次生产，足够则继续
        ２.取原料、生产、输出

    参数：
        inn : in number, 即生产需要的原料个数
        outn: out number, 即inn个原料生产的产品个数
        t: 实际生产所需要的时间
        idn: 生产出的产品的id号
    """

    def produce(self, inn=1, outn=1, t=1.0, idn=0):
        qs = []

        # 原料不足，该次生产失败
        if self.sin.qsize() < inn:
            sleep(1)        # 原料不足，等待１秒　　
            print self.name, idn
            # self.loop += 1
            return 0

        # 取原料
        for i in range(inn):
            qt = self.sin.get()
            qs.append([qt[0], qt[1], qt[2]])
            # print 'qtqs:', qt, qs

        # 生产
        # ts = time.ctime(time.time())  # 记录开始时间
        # sleep(t)                      # 实际生产时间
        # te = time.ctime(time.time())  # 记录结束时间
        ts = self.getTime()
        sleep(t)
        te = self.getTime()

        # 输出（到记录文件和可供下一环节使用的队列）
        for i in range(outn):
            r = [self.name, idn, 'nt', ts, te, qs]
            print >> self.f, r   # 输出重定向：将r输出到self.f指定的记录文件
            self.sout.put(r)     # 输出产品到队列，供下一环节使用
        return 1        # 成功完成一次生产

    def run(self):
        print 'start run ', self.name
        i = 0
        while i < self.loop:
            # for i in range(self.loop):
            i += self.produce(self.inn, self.outn, self.t, i)



"""
***********传输操作****************
功能：
    将生产者a的输出队列传输给生产者b(作为b的输入队列)
参数：
    name:传输器的名称
    a: 起点生产者
    b: 终点生产者

"""

class Transporter(threading.Thread):
    def __init__(self, name, a, b, loop, t=1.0):
        threading.Thread.__init__(self)
        self.name = name
        self.a = a
        self.b = b
        self.loop = loop
        self.f = open(name, 'w')
        self.t = t
        self.timeRate = settings.TIMERATE
        self.startime = settings.STARTIME

    def getTime(self):
        now = datetime.datetime.now()
        delta = (now - self.startime).seconds * self.timeRate
        tmp = self.startime + datetime.timedelta(seconds=delta)
        return tmp.strftime("%Y-%m-%d %H:%M:%S")

    def trans(self, num=1, t=1.0):
        # print 'st'
        qa = self.a.getPQueue()
        qb = self.b.getInOueue()
        # print qa.qsize(),qb.qsize()
        if qa.empty() == False and qb.full() == False:   # 这里应该是 and!!!!!!!!!!!!!!!!!!!!!!!!!1
            qt = qa.get()
            ts = self.getTime()
            sleep(t)
            te = self.getTime()
            qt[2] = 't'
            r = [self.a.name, self.b.name, ts, te, [qt[0], qt[1], qt[2]]]
            print >> self.f, r
            qb.put(qt)
            return 1
        else:
            # print 'else'
            sleep(1)
            # self.loop+=1
            return 0
        pass

    def run(self):
        print 'start trans ', self.name
        # for i in range(self.loop):
        i = 0
        while i < self.loop:        # loop控制整个程序的执行的时间，可以加以扩展，改成时序的！！！！
            # print >> self.f, 'trans:',i
            i += self.trans(1, self.t)


def main2():
    # settings.STARTIME = datetime.datetime.now()

    #
    # p0 = Producer('p0', 20, 0, 1, 0.5, 8)
    # p1 = Producer('p1', 20, 0, 1, 0.5, 4)
    # p2 = Producer('p2', 20,)
    # p3 = Producer()
    # p4 = Producer()
    # p5 = Producer()
    # p6 = Producer()
    # p7 = Producer()
    # p8 = Producer()
    # t0 = Transporter()
    # t1 = Transporter()
    # t2 = Transporter()


    p0 = Producer('p0', 20, 0, 1, 1, 20)
    p1 = Producer('p1', 20, 2, 1, 1, 10)
    p2 = Producer('p2', 20, 2, 1, 2, 5)
    t0 = Transporter('t0', p0, p1, 20)
    t1 = Transporter('t1', p1, p2, 10)
    threads = [p0, p1, p2, t0, t1]

    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join()
    print 'all Done'

if __name__ == '__main__':
    main2()
    pass
















# # import graphlab as gl
# from graphlab import SFrame, SGraph
# import time
# # import urllib
# # urllib.urlretrieve('http://s3.amazonaws.com/dato-datasets/millionsong/song_data.csv', 'songs_data.csv')
# # Jbonds = SFrame.read_csv("bond_edges.csv")
# # Jbonds = SFrame.read_csv('http://s3.amazonaws.com/dato-datasets/bond/bond_vertices.csv')
# # Jbonds.save('bond_vertices.csv')
# edge_data = SFrame.read_csv('bond_edges.csv')
# vertex_data = SFrame.read_csv('bond_vertices.csv')
# g = SGraph(vertices=vertex_data, edges=edge_data, vid_field='name', src_field='src', dst_field='dst')
# g.show(vlabel='id', arrows=True)
# time.sleep(20)
# # usage_data = SFrame.read_csv(
# #     "http://s3.amazonaws.com/dato-datasets/millionsong/10000.txt",
# #     header=False,
# #     delimiter='\t',
# #     column_type_hints={'X3': int}
# # )
# # usage_data.save('./music_usage_data')
#


