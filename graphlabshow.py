# -*- coding: UTF-8 -*-# import graphlab as gl
from graphlab import SFrame, SGraph
from time import *
import settings

"""
***************graphLab溯源***************
功能：
    根据要求显示某一指定产品的生产运输轨迹(显示整图＝同时溯源所有最终产品)
原理：
    生成构成图的点文件和边文件(tmp_vertices.csv 和　tmp_edges.csv)
使用：
    1. clearShowfile　清空之前的临时文件（tmp_vertices.csv 和　tmp_edges.csv）内容
    2. createShowfile 创建并格式化临时文件
    3. createCSV([path],[id_list])　生成指定对象的溯源数据,写入临时文件
        [path]: 溯源对象数据的保存文件名（生产者名称）
        [id_list]: 溯源对象的id列表
    4. showPath　显示溯源路径

"""

class graphShow():
    def __init__(self):
        self.edgesFn = settings.EDGES_FILENAME
        self.verticesFn = settings.VERTICES_FILENAME
        self.highlight = []
        pass

    def createShowfile(self):
        with open(self.edgesFn, 'a') as wr:
            wr.write('src,dst,relation')
        with open(self.verticesFn, 'a') as wr:
            wr.write('name,attributes')
        pass

    def clearShowfile(self):
        with open(self.edgesFn, 'w') as wr:
            wr.write('')
        with open(self.verticesFn, 'w') as wr:
            wr.write('')

    """
    # 功能： BSprocess　生成溯源过程中某一原子段的数据
    # 参数：
            line:　保存当前节点的具体数据
            dst : 当前点的名称 (文件名_id)
    # 原理：
            如果当前点有父节点，则对每个父节点分情况考虑：
            １. 父节点经过运输到达的，生成父节点的镜像节点(文件名_id_t)并写入点文件,再将一条运输边和一条生产边写入边文件
            ２. 父亲节点没有经过运输到达的，只写入一条生产边到边文件
    """
    def BSprocess(self, line, dst):
        with open(self.edgesFn, 'a') as Ewr:
            with open(self.verticesFn, 'a') as Vwr:
                for i in line[5]:
                    newdst = i[0] + '_' + str(i[1])
                    # Vwr.write('\n' + newdst + ' ' + 'no description')
                    if i[2] == 't':
                        Tnewdst = newdst + '_' + 't'
                        Vwr.write('\n' + Tnewdst + ',' + 'no description')  # 注意空格
                        Ewr.write('\n' + newdst + ',' + Tnewdst + ',' + 't')
                        Ewr.write('\n' + Tnewdst + ',' + dst + ',' + 'p')
                    elif i[2] == 'nt':
                        Ewr.write('\n' + newdst + ',' + dst + ',' + 'p')
        pass


    """
    # createCSV([path],[id_list])
    # 功能：
        生成指定对象的溯源数据,写入临时文件
      参数：
        [path]: 溯源对象数据的保存文件名（生产者名称）
        [id_list]: 溯源对象的id列表
    　原理：
        利用递归结构, 根据指定点,从后向前遍历溯源路径
    """

    def createCSV(self, path, p):
        with open(path, 'r') as rd:
            lines = rd.readlines()
        for line in lines:
            line = eval(line)
            if line[1] in p:    # 判空操作
                dst = line[0] + '_' + str(line[1])
                with open(self.verticesFn, 'a') as wr:
                    wr.write('\n' + dst + ',' + 'no description')  # 写入当前点
                parentLine = line[5]
                if parentLine == []:
                    return
                else:
                    if len(parentLine) > 2:
                        self.highlight.append(dst)
                    self.BSprocess(line, dst)
                    for item in parentLine:
                        self.createCSV(item[0], [item[1]])
                pass

        pass

    def showPath(self, highlight=None):
        edge_data = SFrame.read_csv(self.edgesFn)
        vertex_data = SFrame.read_csv(self.verticesFn)
        g = SGraph(vertices=vertex_data, edges=edge_data, vid_field='name', src_field='src', dst_field='dst')
        g.show(vlabel='id', elabel='relation',highlight=highlight, arrows=True)  # highLight
        sleep(10)
        pass

if __name__ == '__main__':
    # *********关于时间操作的测试***************
    #
    # import datetime
    # def countime():
    #     starttime = datetime.datetime.now()
    #     return starttime
    #     pass
    #
    # starttime = datetime.datetime.now()
    # # long running
    # sleep(1)
    # endtime = datetime.datetime.now()
    # print 'diifs:', (endtime - starttime).seconds
    # d1 = datetime.datetime.now()
    # d2 = countime()
    # d3 = d1 + datetime.timedelta(seconds=100)
    # print 'now:', d1, '\n100 sec later:', d3.strftime("%Y-%m-%d %H:%M:%S")
    # print 'now func:', d2


    # ***************关于递归写文件操作的测试**********************
    #
    # def mywr():
    #     with open('test.txt', 'a') as wr:
    #         wr.write('line3\n')
    # with open('test.txt', 'a') as wr:
    #     wr.write('line1\n')
    #     wr.write('line2\n')
    #     mywr()


    # ***************graphLab显示的测试***************************

    testShow = graphShow()
    testShow.clearShowfile()
    testShow.createShowfile()
    testShow.createCSV('p4', [1])
    testShow.showPath(testShow.highlight)

    pass

