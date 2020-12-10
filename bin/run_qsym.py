#!/usr/bin/env python2
# coding=utf-8
import argparse
import logging
import os
import shutil
from qsym import Executor, utils

l = logging.getLogger('[run_qsym]')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-i", dest="input_file", help="An input file", required=True)
    p.add_argument("-t", dest="tmp_dir", help="An tmp directory", required=True)
    p.add_argument("-o", dest="output_dir", help="An afl output directory", required=True)
    p.add_argument("-b", dest="bitmap", help="A bitmap file")
    p.add_argument("cmd", nargs="+",
            help="Command to execute: use %s to denote a file" % utils.AT_FILE)
    return p.parse_args()

def mkdir(dirp):
    if not os.path.exists(dirp):
        os.makedirs(dirp)

def main():
    args = parse_args()
    # 创建qsym需要的目录
    qsymDir = os.path.join(args.output_dir, "qsym")
    qsymQueue = os.path.join(qsymDir, "queue")
    mkdir(qsymDir)
    mkdir(qsymQueue)
    # 当前文件
    cur_input = os.path.realpath(os.path.join(args.output_dir, ".cur_input"))
    # 这个input_file是一个文件带有id记录的
    target = args.input_file
    shutil.copy2(target, cur_input)
    l.debug("Run qsym : input=%s" % target)

    # 运行
    q = Executor(args.cmd,
            cur_input,
            args.tmp_dir,
            args.bitmap,
            argv=["-l", "1"])
    ret = q.run()
    l.debug("Total=%d s, Emulation=%d s, Solver=%d s, Return=%d"
                 % (ret.total_time,
                    ret.emulation_time,
                    ret.solving_time,
                    ret.returncode))

    # 获取种子
    src_id = os.path.basename(target)[:len("id:......")]
    num_testcase = 0
    for testcase in q.get_testcases():
        num_testcase +=1
        #todo 精简种子
        filename = os.path.join(qsymQueue, "id:%06d,src:%s"%(num_testcase, src_id))
       # shutil.copy2(testcase, filename)
        shutil.move(testcase, filename)
        l.debug("Creating: %s" %filename)

    # try:
    #     os.rmdir(q.testcase_directory)
    # except Exception:
    #     pass

    l.debug("Generate %d testcases " % num_testcase)





if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
