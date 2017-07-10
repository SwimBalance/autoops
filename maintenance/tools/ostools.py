
import paramiko


class Task(object):
	def __init__(self, task_info):
		self.task_info = task_info
	def create_connect(self):
		# 创建SSH对象
		connectObj = paramiko.SSHClient()
		# 把要连接的机器添加到known_hosts文件中
		connectObj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		# 连接服务器
		connectObj.connect(
			hostname=self.task_info['ip'],
			username=self.task_info['user'],
			password=self.task_info['pwd'],
			port=22,
			timeout=10
		)
		# 判断是否连接成功
		###################
		return connectObj

	def execute(self):
		try:
			connectObj = self.create_connect()
		except:
			return '连接失败'
		cmd = self.task_info['cmd']
		stdin, stdout, stderr = connectObj.exec_command(cmd)
		result = stdout.read()
		connectObj.close()
		if not result:
			result = stderr.read()
		return result.decode()
