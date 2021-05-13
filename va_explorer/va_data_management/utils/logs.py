#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  6 14:01:55 2021

@author: babraham
"""
import logging

def write_va_log(logger, msg, request=None, logtype="info", session_key=None):
    log_fns = {"info": logger.info,"debug": logger.debug}
    if not request and not session_key:
        raise ValueError("Must provide either session_key or request object to pull session_key from")
    if not session_key:
        session_key = request.session.session_key
    msg = f"SID: {session_key} - " + msg
    log_fn = log_fns.get(logtype.lower(), logger.info)
    log_fn(msg)
    