# _*_ coding: utf-8 _*_

__author__ = "joyce"

import logging  
import os
import time


def make_log_dir(log_dir):
    """
    创建log文件夹
    """
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)


class Logger(object):
  
    def __init__(self, logger):
        """ 
        指定保存日志的文件路径，日志级别，以及调用文件 
            将日志存入到指定的文件中 
        :param logger: 
        """  
        # 创建一个logger  
        self.logger = logging.getLogger(logger)  
        self.logger.setLevel(logging.DEBUG)  
  
        # 创建一个handler，用于写入日志文件  
        rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        log_path = os.getcwd() + '/Logs/'
        make_log_dir(log_path)
        log_name = log_path + rq + '.log'
        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.INFO)  
  
        # 再创建一个handler，用于输出到控制台  
        ch = logging.StreamHandler()  
        ch.setLevel(logging.INFO)  
  
        # 定义handler的输出格式  
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
        fh.setFormatter(formatter)  
        ch.setFormatter(formatter)  
  
        # 给logger添加handler  
        self.logger.addHandler(fh)  
        self.logger.addHandler(ch)  
  
    def getlog(self):
        return self.logger

