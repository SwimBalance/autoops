#!/usr/bin/env python
# coding=utf-8
import json
import logging
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


class ResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)

    def _get_return_data(self, result):
        try:
            if result.get('msg'):
                return_data = result.get('msg')
                print(1)
            elif result.get('stderr'):
                return_data = result.get('stderr')
                print(2)
            else:
                return_data = result
                print(3)
        except:
            pass
        return return_data

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        self.runner_on_ok(host, result._result)
        print(result.task_name,host,result._result['stdout'])
        return_data = self._get_return_data(result._result)
        # print(result._result)
        # logging.warning('===v2_runner_on_ok====host=%s===result=%s' % (host, return_data))
        # print(return_data.keys())
        # print(result.keys())


    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        self.runner_on_failed(host, result._result, ignore_errors)
        return_data = self._get_return_data(result._result)
        logging.warning('===v2_runner_on_failed====host=%s===result=%s' % (host, return_data))


    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self.runner_on_unreachable(host, result._result)
        return_data = self._get_return_data(result._result)
        logging.warning('===v2_runner_on_unreachable====host=%s===result=%s' % (host, return_data))


    def v2_runner_on_skipped(self, result):
        if C.DISPLAY_SKIPPED_HOSTS:
            host = result._host.get_name()
            self.runner_on_skipped(host, self._get_item(getattr(result._result, 'results', {})))
            logging.warning("this task does not execute,please check parameter or condition.")


    def v2_playbook_on_stats(self, stats):
        logging.warning('===========palybook executes completed========')


class AnsibleAPI(object):
    def __init__(self, hostlist, playbooks, *args, **kwargs):
        self.hostlist = hostlist
        self.playbooks = playbooks
        # self.inventory = None
        # self.variable_manager = None
        # self.loader = None
        # self.options = None
        self.passwords = None
        self.callback = None
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
        playbook._tqm._stdout_callback = ResultsCollector()
        playbook.run()


# hostlist = ['10.26.222.210']
# playbooks = ['/tempdir/ancode/test.yml']
# pl = AnsibleAPI(hostlist, playbooks)
# pl.runplaybook()
