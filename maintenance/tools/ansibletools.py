#!/usr/bin/env python
# coding=utf-8
import json
import logging

import datetime
import time
from django.db import connection
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from collections import namedtuple
from ansible import constants as C
import ansible.executor.task_result


# t0 = tn = time.time()
# def timestamp(self):
#     if self.current is not None:
#         self.stats[self.current]['time'] = time.time() - self.stats[self.current]['time']
#
# from ansible.compat.six.moves import reduce
#
# def secondsToStr(t):
#     # http://bytes.com/topic/python/answers/635958-handy-short-cut-formatting-elapsed-time-floating-point-seconds
#     rediv = lambda ll, b: list(divmod(ll[0], b)) + ll[1:]
#     return "%d:%02d:%02d.%03d" % tuple(reduce(rediv, [[t * 1000, ], 1000, 60, 60]))
#
#
# def filled(msg, fchar="*"):
#     if len(msg) == 0:
#         width = 79
#     else:
#         msg = "%s " % msg
#         width = 79 - len(msg)
#     if width < 3:
#         width = 3
#     filler = fchar * width
#     return "%s%s " % (msg, filler)
#
#
# def tasktime():
#     global tn
#     time_current = time.strftime('%A %d %B %Y  %H:%M:%S %z')
#     time_elapsed = secondsToStr(time.time() - tn)
#     time_total_elapsed = secondsToStr(time.time() - t0)
#     tn = time.time()
#     return filled('%s (%s)%s%s' % (time_current, time_elapsed, ' ' * 7, time_total_elapsed))
#


class ResultsCollector(CallbackBase):
    def __init__(self, taskid, system, processname):
        super(ResultsCollector, self).__init__()
        self.taskid = taskid
        self.system = system
        self.processname = processname
        self.current = None
        self.stats = {}

    def _get_return_data(self, result):
        try:
            if result.get('msg'):
                return_data = result.get('msg')
                # print(1)
            elif result.get('stderr'):
                return_data = result.get('stderr')
                # print(2)
            else:
                return_data = result
                # print(3)
        except:
            pass
        return return_data

    def _record_task(self, task):
        """
        Logs the start of each task
        """
        print("Logs the start of each task")
        # self._display.display(tasktime())
        # timestamp(self)

        # Record the start time of the current task
        # self.current = task._uuid
        # self.stats[self.current] = {'time': time.time(), 'name': task.get_name()}
        # if self._display.verbosity >= 2:
        #     self.stats[self.current][ 'path'] = task.get_path()

    # def _record_task(self, task):
    #     """
    #     Logs the start of each task
    #     """
    #     self._display.display(tasktime())
    #     timestamp(self)
    #
    #     # Record the start time of the current task
    #     self.current = task._uuid
    #     self.stats[self.current] = {'time': time.time(), 'name': task.get_name()}
    #     if self._display.verbosity >= 2:
    #         self.stats[self.current]['path'] = task.get_path()

    # 与playbook_on_stats对应，每台服务器task调用开始时调用的函数
    # def playbook_on_start(self):
    #     pass
    #     print("playbook_on_start!")

    # 每台服务器每个task开始时调用的函数，运行完之后调用v2_runner_on_ok等函数
    def playbook_on_task_start(self, name, is_conditional):
        processname = self.processname
        taskname = name
        taskid = self.taskid
        systemname = self.system
        self.stats[processname, taskname] = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
        #print("playbook_on_task_start!", taskname, processname, self.stats)
        sqlstatement = "insert into checksystem(taskid,taskname,starttime,systemname,processname) " \
                       "VALUES ('%s', '%s', '%s', '%s', '%s')" % (
                           self.taskid, taskname, self.stats[processname, taskname], self.system, processname)
        #print(sqlstatement)
        with connection.cursor() as cursor:
            cursor.execute(sqlstatement)
            connection.close()

    # 一台机器的所有task执行之后调用的函数
    def playbook_on_stats(self, stats):
        processname = self.processname
        taskid = self.taskid
        systemname = self.system
        endtime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
        sqlstatement = "update checksystem set endtime='%s' where id=(select a.id from ((select max(id) as id from checksystem where taskid='%s' and processname='%s' and systemname='%s') a))"%(endtime,taskid,processname,systemname)
        #print(sqlstatement)
        with connection.cursor() as cursor:
            cursor.execute(sqlstatement)
        # Record the timing of the very last task
        #print("playbook_on_stats")

    # 与playbook_on_stats对应，每台服务器task调用开始时调用的函数，在playbook_on_start后运行
    # def playbook_on_play_start(self, name):
    #     print("playbook_on_play_start", name)
    #每个task正常运行后调用该函数
    def v2_runner_on_ok(self, result):
        processname = self.processname
        taskid = self.taskid
        taskname = result.task_name
        #print(processname + "=====v2_runner_on_ok======")
        ipaddress = result._host
        res = result._result['stdout_lines']
        status = 'OK'
        # sqlstatement = "insert into checksystem(taskid,ipaddress,result,taskname,starttime,endtime,status,systemname) " \
        #                "VALUES ('%s', '%s', \"%s\", '%s', '%s', '%s', '%s', '%s')" % (
        #                    self.taskid, ipaddress, res, taskname, start, end, status, self.system)
        sqlstatement = "update checksystem set result =\"%s\" ,ipaddress='%s',status='%s' where taskid='%s' and taskname='%s' and processname='%s' " % (
            res, ipaddress, status, taskid, taskname, processname)
        #print(sqlstatement)
        sql_tasksummary="update tasksummary set taskcurrent=taskcurrent+1 where taskid='%s' and ipaddress='%s'"%(taskid,ipaddress)
        #print("sql_tasksummary=",sql_tasksummary)
        with connection.cursor() as cursor:
            cursor.execute(sqlstatement)
            cursor.execute(sql_tasksummary)
            connection.close()
    #task运行failed调用该函数
    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        self.runner_on_failed(host, result._result, ignore_errors)
        return_data = self._get_return_data(result._result)
        # print(result)
        logging.warning('===v2_runner_on_failed====host=%s===result=%s' % (host, return_data))

    # host无法访问时调用该函数
    def v2_runner_on_unreachable(self, result):
        ipaddress = result._host
        # # print('taskid = '+ self.taskid)
        # taskname = result.task_name
        # # print(result._result.keys())
        # start = result._result['start']
        # end = result._result['end']
        # res = result._result['stdout_lines']
        print(ipaddress, result._result)
        status = 'UNREACHABLE'
        # print(status)
        # sqlstatement = "insert into checksystem(taskid,ipaddress,result,taskname,starttime,endtime,status,systemname) " \
        #                "VALUES ('%s', '%s', \"%s\", '%s', '%s', '%s', '%s', '%s')" % (
        #                    self.taskid, ipaddress, res, taskname, start, end, status, self.system)
        # print(sqlstatement)
        # with connection.cursor() as cursor:
        #     cursor.execute(sqlstatement)
        #     logging.warning('===v2_runner_on_unreachable====host=%s===result=%s' % (host, return_data))
        #
        #
        # def v2_runner_on_skipped(self, result):
        #     if C.DISPLAY_SKIPPED_HOSTS:
        #         host = result._host.get_name()
        #         self.runner_on_skipped(host, self._get_item(getattr(result._result, 'results', {})))
        #         logging.warning("this task does not execute,please check parameter or condition.")
        #
        #
        # def v2_playbook_on_stats(self, stats):
        #     logging.warning('===========palybook executes completed========')


class AnsibleAPI(object):
    def __init__(self, hostlist, playbooks, uuid, systemname, processname, *args, **kwargs):
        self.hostlist = hostlist
        self.playbooks = playbooks
        # self.inventory = None
        # self.variable_manager = None
        # self.loader = None
        # self.options = None
        self.processname = processname
        self.passwords = None
        self.callback = None
        self.taskid = uuid
        self.system = systemname
        #     self.__initializeData()
        #
        # def __initializeData(self):
        Options = namedtuple('Options', ['connection', 'remote_user', 'ask_sudo_pass', 'verbosity', 'ack_pass',
                                         'module_path', 'forks', 'become', 'become_method', 'become_user',
                                         'check', 'listhosts', 'listtasks', 'listtags', 'syntax',
                                         'sudo_user', 'sudo'])

        self.options = Options(connection='smart', remote_user='root', ack_pass=None, sudo_user='root',
                               forks=200, sudo='yes', ask_sudo_pass=False, verbosity=5, module_path=None,
                               become=True, become_method='su', become_user='root', check=None, listhosts=False,
                               listtasks=False, listtags=None, syntax=None)
        self.loader = DataLoader()
        self.variable_manager = VariableManager()
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager,
                                   host_list=self.hostlist)
        # host_list=['10.26.222.210'])
        self.variable_manager.set_inventory(self.inventory)
        self.variable_manager.extra_vars = {"ansible_ssh_user": "root"}  # 额外参数，包括playbook参数 key:value

    def runplaybook(self):
        playbook = PlaybookExecutor(  # playbooks=['/tempdir/ancode/test.yml'],
            playbooks=self.playbooks,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=None)
        playbook._tqm._stdout_callback = ResultsCollector(self.taskid, self.system, self.processname)
        playbook.run()

# hostlist = ['10.26.202.133']
# playbooks = ['/tempdir/ancode/test.yml']
# pl = AnsibleAPI(hostlist, playbooks)
# pl.runplaybook()
