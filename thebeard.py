import os
import glob
import time
from operator import itemgetter
from itertools import groupby

cdr = os.path.split(os.path.realpath('thebeard.py'))[0]
#print('CURRENT DIR = ' + cdr + '\n')
rd = cdr + '/running/'
pd = cdr + '/pending/'
#print('RUNNING DIR = ' + rd + '\n')
#print('PENDING DIR = ' + rd + '\n')

def padstr(instr, pad, padlen) :
    #print('FN: padstr(%s,%s,%i)' %(instr, pad, padlen))
    dif = (padlen - len(instr)) + 1
    o = instr
    for i in range(1,dif) :
        o = o + pad
    #print('\t'+o)
    return(o)


def getjobs(p) :
	if os.path.isdir(p) :
		subs = os.listdir(p)
		#print("subdirs="  + str(subs))
		shs = glob.glob(p + '*.sh*')
		for u in subs :
			#print("checking: " + p + u)
			sshs = glob.glob((p + u) + '/*.sh*')
			shs = shs + sshs
		#print("shs="+str(shs))
		a = []
		for s in shs :
			fp = s.split('_')
			#print('time  = ' + (fp[0]+fp[1]).split('/')[-1:][0])
			#print('frame = ' + fp[2])
			#print('job   = ' + fp[3])
			#print('shot  = ' + fp[4])
			#print('scene = ' + fp[4])
			#print('rop   = ' + fp[5].split('.')[0])
			a.append({'time':(fp[0]+fp[1]).split('/')[-1:][0], 'frame':fp[2], 'job':fp[3], 'shot':fp[4], 'scene':fp[4], 'rop':('_'.join(fp[5:]).split('.')[0])})
		return(a)


def calcjobs (a) :
	o = []
	sbb = sorted(a, key=itemgetter('time'))
	maxlen = 0
	for okey, ogroup in groupby(sbb, key=lambda x:x['shot']):
		og = list(ogroup)
		shotline = (' shot...: ' + okey)
		shotlen = len(shotline)
		if shotlen > maxlen : maxlen = shotlen
		o.append([shotline, str(len(og))])
		og = sorted(og, key=itemgetter('scene'))
		for skey, sgroup in groupby(og, key=lambda x:x['scene']):
			sg = list(sgroup)
			sceneline = ('  +scene: ' + skey)
			scenelen = len(sceneline)
			if scenelen > maxlen : maxlen = scenelen
			o.append([sceneline, str(len(sg))])
			sg = sorted(sg, key=itemgetter('rop'))
			for rkey, rgroup in groupby(sg, key=lambda x:x['rop']):
				rg = list(rgroup)
				ropline = ('   +rop.: ' + rkey)
				roplen = len(ropline)
				if roplen > maxlen : maxlen = roplen
				o.append([ropline, str(len(rg))])
	return (o, maxlen)

def listjobs(a) :
	o = ""
	for i in a[0] :
		pline = padstr(i[0],".",a[1])
		o = o + (pline + ' : ' + i[1]) + '\n'
	return o
	
bb = getjobs(pd)
rr = getjobs(rd)


jr = calcjobs(rr)
jp = calcjobs(bb)
lr = listjobs(jr)
lb = listjobs(jp)

print('running\n' + lr + '\npending\n' + lb)


