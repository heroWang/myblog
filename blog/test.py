#! /usr/bin/env python
import functools
import inspect

def log(func):
  def wrapper(*args,**kwargs):
    #print args,kwargs
    # do some log
    print 'logging...'
    return func(*args,**kwargs)
  return functools.wraps(func)(wrapper)

def log2(func):
  def wrapper(*args,**kwargs):
    #print args,kwargs
    # do some log
    print 'logging 2...'
    return func(*args,**kwargs)
  return functools.wraps(func)(wrapper)

@log
@log2
def func(content):
  print "print : "+content

if __name__ == '__main__':
  func('hello decrator.')
  print func.__name__
  print inspect.getargspec(func)
  #print "----------equals to------------"
  #log(func)(None)

#ignore for rsync test
