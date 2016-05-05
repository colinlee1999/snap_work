import sys
import json
import demjson

def main():
  a = [1, 2, 3]
  b = [4, 5, 6]
  s1 = {'a': a}
  s2 = {'b': b}
  data = [s1, s2]
#  jsonData = demjson.encode(data)
  jsonData = data
  outFile = open('test.json', 'w')
  json.dump(jsonData, outFile)

def happy():
  for i in range(5):
    print i,
  print '6'
  a = 7
  print a,
  b = 8
  print b


if __name__ == '__main__':
  sys.exit(int(main() or 0))
