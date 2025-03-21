#!/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf-8 vi:ts=5:sw=5:expandtab:ft=python
"""
test jit cases
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(os.getcwd())), "utils"))

from utils.yaml_loader import YamlLoader
from jittrans import JitTrans

yaml_path = os.path.join(os.path.abspath(os.path.dirname(os.getcwd())), "yaml", "base.yml")
yml = YamlLoader(yaml_path)


def test_mean_5():
    """test mean_5"""
    jit_case = JitTrans(case=yml.get_case_info("mean_5"))
    jit_case.jit_run()
