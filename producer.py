#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on March 31, 2016

@author: maobo, Tengwei

producer, consumer and transporter simulation

模拟生产者，消费者与运输者，并输出相关记录，用于溯源分析

'''

#coding=cp936
from random import randint
from graphlabshow import *
from time import sleep
from Queue import Queue
import threading
import datetime
import settings

class Producer(threading.Thread):
    def __init__(self, name="", qn=20, t=1.0, loop=10, recipe=None):
        threading.Thread.__init__(self)
        self.name = name
        self.recipe = recipe
        self.t = t
        self.f = open(name, 'w')        #
        self.loop = loop
        self.startime = settings.STARTIME
        self.timeRate = settings.TIMERATE
        self.sout = Queue(qn)
        self.sin = {}
        for k in self.recipe:
           self.sin[k] = Queue(qn)

    def getPQueue(self):        # producer 的输出队列
        return self.sout

    def getInOueue(self, k):       # producer 的输入队列
        return self.sin[k]

    def getTime(self):
        now = datetime.datetime.now()
        delta = (now - self.startime).seconds * self.timeRate
        tmp = self.startime + datetime.timedelta(seconds=delta)
        return tmp.strftime("%Y-%m-%d %H:%M:%S")
        pass


    def MtJudge(self):
        for k in self.sin:
            if (self.sin)[k].qsize() < self.recipe[k]:
                return False
        return True
        pass

    """
    *************produce:生产操作****************
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
    def produce(self, t=1.0, idn=0):
        qs = []

        # 原料不足，该次生产失败
        if self.MtJudge() == False:
            sleep(1)        # 原料不足，等待１秒　　
            print self.name, idn
            return 0
        # else:
        #     print self.name, idn, 'material enough'

        # 取原料
        print 'yl'
        for k in self.recipe:
            for i in range(self.recipe[k]):
                qt = (self.sin)[k].get()
                qs.append([qt[0], qt[1], qt[2]])
                # print 'qtqs:', qt, qs

        # 生产
        ts = self.getTime()             # 记录开始时间
        sleep(t)                        # 实际生产时间
        te = self.getTime()             # 记录结束时间

        # 输出（到记录文件和可供下一环节使用的队列）
        r = [self.name, idn, 'nt', ts, te, qs]
        print >> self.f, r   # 输出重定向：将r输出到self.f指定的记录文件
        self.sout.put(r)     # 输出产品到队列，供下一环节使用
        return 1        # 成功完成一次生产

    def run(self):
        print 'start run ', self.name
        i = 0
        while i < self.loop:
            # for i in range(self.loop):
            i += self.produce(self.t, i)
        self.f.close()



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
        qb = self.b.getInOueue(self.a.name)
        # print qa.qsize(),qb.qsize()
        if qa.qsize() >= self.b.recipe[self.a.name] and qb.full() == False:   # 这里应该是 and!!!!!!!!!!!!!!!!!!!!!!!!!1
            qs = []
            for k in range(self.b.recipe[self.a.name]):
                qt = qa.get()
                qs.append(qt)
            ts = self.getTime()
            sleep(t)
            te = self.getTime()
            qtRec = []
            for qt in qs:
                qt[2] = 't'
                qtRec.append([qt[0], qt[1], qt[2]])
                qb.put(qt)
            r = [self.a.name, self.b.name, ts, te, qtRec]
            print >> self.f, r
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
        while i < self.loop:
            # print >> self.f, 'trans:',i
            i += self.trans(1, self.t)


class BSModel():
    def __init__(self):
        self.graphModel = settings.GRAPHMODEL
        self.threads = []
        pass
    def CreateModel(self):
        for i in self.graphModel:
            if i[0] == 'p':
                p = Producer(i[1], i[2], i[3], i[4], i[5])
                self.threads.append(p)
            elif i[0] == 't':
                t = Transporter(i[1], self.threads[i[2]], self.threads[i[3]], self.threads[i[3]].loop)
                self.threads.append(t)
        pass

    def runModel(self):
        for i in range(len(self.threads)):
            self.threads[i].start()
        for i in range(len(self.threads)):
            self.threads[i].join()
        print 'all Done'
        pass

    def showBSgraph(self, pointName, idList):
        testShow = graphShow()
        testShow.clearShowfile()
        testShow.createShowfile()
        testShow.createCSV(pointName, idList)    # 'p4', [1]
        testShow.showPath(testShow.highlight)
        pass
    pass

# def main2():
#
#     p0 = Producer('p0', 20, 1, 8, {})
#     p1 = Producer('p1', 20, 1, 4, {})
#     p2 = Producer('p2', 20, 1, 4, {'p0': 2, 'p1': 1})
#     p3 = Producer('p3', 20, 1, 16, {})
#     p4 = Producer('p4', 20, 0.5, 4, {'p2': 1, 'p3': 4})
#     p5 = Producer('p5', 20, 1, 12, {})
#     p6 = Producer('p6', 20, 1, 4, {})
#     p7 = Producer('p7', 20, 0.5, 4, {'p5': 3, 'p6': 1})
#     p8 = Producer('p8', 20, 1, 2, {'p4': 2, 'p7': 2})
#     t0 = Transporter('t0', p0, p2, p2.loop)
#     t1 = Transporter('t1', p1, p2, p2.loop)
#     t2 = Transporter('t2', p2, p4, p4.loop)
#     t3 = Transporter('t3', p3, p4, p4.loop)
#     t4 = Transporter('t4', p4, p8, p8.loop)
#     t5 = Transporter('t5', p5, p7, p7.loop)
#     t6 = Transporter('t6', p6, p7, p7.loop)
#     t7 = Transporter('t7', p7, p8, p8.loop)
#     threads = [p0, p1, p2, p3, p4, p5, p6, p7, p8, t0, t1, t2, t3, t4, t5, t6, t7]
#     for i in range(len(threads)):
#         threads[i].start()
#     for i in range(len(threads)):
#         threads[i].join()
#     print 'all Done'
#     pass

if __name__ == '__main__':
    bs = BSModel()
    bs.CreateModel()
    bs.runModel()
    bs.showBSgraph('p4', [1])

    pass
