import pytest
from scrapper import *

def test_bad_thread():
    args=['scrapper.py', 'http://domain.com', '-o', 'filename', '-t', 'bad', '--maxurls', '100', '--timeout', '1', '--verify', 'False']
    opt = 'ot'
    long_opt = ['maxurls','timeout','verify']
    opts,args = getopt.gnu_getopt(args[2:],opt,long_opt)
    #This should rise a TypeError exception
    try:
        set_options(opts,args)    
    except Exception as exp:
        assert(type(exp) == TypeError)

def test_bad_crawl():
    args=['scrapper.py', 'http://domain.com', '-o', 'filename', '-t', '4', '--maxurls', 'bad', '--timeout', '1', '--verify', 'False']
    opt = 'ot'
    long_opt = ['maxurls','timeout','verify']
    opts,args = getopt.gnu_getopt(args[2:],opt,long_opt)
    #This should rise a TypeError exception
    try:
        set_options(opts,args)    
    except Exception as exp:
        assert(type(exp) == TypeError)

def test_bad_timeout():
    args=['scrapper.py', 'http://domain.com', '-o', 'filename', '-t', '4', '--maxurls', '100', '--timeout', 'bad', '--verify', 'False']
    opt = 'ot'
    long_opt = ['maxurls','timeout','verify']
    opts,args = getopt.gnu_getopt(args[2:],opt,long_opt)
    #This should rise a TypeError exception
    try:
        set_options(opts,args)    
    except Exception as exp:
        assert(type(exp) == TypeError)

def test_bad_sslverify():
    args=['scrapper.py', 'http://domain.com', '-o', 'filename', '-t', '4', '--maxurls', '100', '--timeout', '1', '--verify', 'bad']
    opt = 'ot'
    long_opt = ['maxurls','timeout','verify']
    opts,args = getopt.gnu_getopt(args[2:],opt,long_opt)
    #This should rise a TypeError exception
    try:
        set_options(opts,args)    
    except Exception as exp:
        assert(type(exp) == TypeError)

def test_unreachable_URL():
    url='htt:bad.host.m'
    error_string = f'Could not fetch url: \033[4m{url}\033[0m.'
    print(error_string)
    #This host should return a non-reachable message
    response = request_url(url) 
    assert(response == -1)
    
    
