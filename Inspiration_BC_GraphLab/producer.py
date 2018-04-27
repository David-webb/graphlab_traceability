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


"""
*************produce:生产操作****************
功能：
    完成产品生产，其过程分为：
    １.原料数量判断，不够则等１秒，然后退出该次生产，足够则继续
    ２.取原料、生产、输出

参数：
    name: 生产者名称
    qn: 生产者输入/输出队列的长度
    t: 实际生产所需要的时间
    loop:　需要生产产品的个数
    recipe: 生产该种产品的配方
"""

class Producer(threading.Thread):
    def __init__(self, name="", qn=20, t=1.0, loop=10, recipe=None):
        threading.Thread.__init__(self)
        self.name = name
        self.recipe = recipe            # 生产配方
        self.t = t
        self.f = open(name, 'w')        #
        self.f.write('')
        self.f.close()
        self.f = open(name, 'a')
        self.loop = loop
        self.startime = settings.STARTIME
        self.timeRate = settings.TIMERATE
        self.sout = Queue(qn)
        self.Sleeptime = settings.SLEEPTIME
        self.sin = {}               # 当前已有原料
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

    def getEnvironInfo(self):
        temperature = randint(20, 30)
        humidity = randint(25, 50)
        videoID = (datetime.datetime.strptime(self.getTime(), "%Y-%m-%d %H:%M:%S")).strftime("%Y%m%d%H%M%S")
        EnInfo = "Temperature: " + `temperature` + '℃ Humidity: ' + `humidity` + '% videoID: ' + videoID
        return EnInfo
        pass


    def MtJudge(self):
        for k in self.sin:
            if (self.sin)[k].qsize() < self.recipe[k]:
                return False
        return True
        pass


    def produce(self, t=1.0, idn=0):
        qs = []

        # 原料不足，该次生产失败
        if self.MtJudge() == False:
            sleep(self.Sleeptime)        # 原料不足，等待１秒　　
            print self.name, idn
            return 0
        # else:
        #     print self.name, idn, 'material enough'

        # 取原料
        for k in self.recipe:
            for i in range(self.recipe[k]):
                qt = (self.sin)[k].get()
                qs.append([qt[0], qt[1], qt[2]])        # 所在文件（pi）, 索引,　类型(p|t)
                # print 'qtqs:', qt, qs

        # 生产
        ts = self.getTime()             # 记录开始时间
        sleep(t)                        # 实际生产时间
        te = self.getTime()             # 记录结束时间

        # 输出（到记录文件和可供下一环节使用的队列）
        # description = self.name + '_' + `idn` +':('+ self.getEnvironInfo() +')'
        description = ''
        r = [self.name, idn, 'nt', ts, te, qs, description]
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
    loop: 运输的趟数
    t：　每次运输的时间

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
        self.Sleeptime = settings.SLEEPTIME

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
            for k in range(self.b.recipe[self.a.name]):         # 每一次运输只运输某一种原料，数量为配方中对应的数量
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
            sleep(self.Sleeptime)
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



"""
***********溯源模型操作****************
功能：
    实现溯源模型的创建,运行和显示
参数：
    主要从settings.py中读取参数

"""
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


if __name__ == '__main__':

    bs = BSModel()
    bs.CreateModel()
    bs.runModel()
    # bs.showBSgraph('p4', range(60))       # 可以对任一生产者的任一产品进行溯源

    # print (end - start).microseconds

    pass
