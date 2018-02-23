# wedge 1 by 1 for local farmit Q in Desktop
# by c.p.brown 2018
###################################################################

import os
import string
import getpass
import time
from datetime import datetime

usr = getpass.getuser()

pathtohoudini = "/opt/hfs" + hou.applicationVersionString()

ops = hou.selectedNodes()


def prepadstr(instr, pad, padlen) :
        dif = (padlen - len(instr)) + 1
        o = ''
        for i in range(1,dif) :
                o = o + pad
        o = o + instr
        #print(o)
        return(o)

if len(ops) >= 1 :

    hscene = hou.hipFile.name()
    hname = hou.hipFile.path().split('.')[0].split('/')[-1]
    hdir = hou.hipFile.path().split('.')[0].split('/')[-3]
    hprj = "/home/" + usr + "/Desktop"
       
    for i in ops :
        isasim = 1
        batchcmd = ""
        otn = i.type().name()
        opth = i.path()
        if otn == 'rop_geometry' or otn == 'rop_dop' or otn == 'geometry' or otn == 'wedge' or otn == 'rop_comp' or otn == 'comp' or otn == 'ifd':
            opn = i.name()
            if otn == 'wedge' :
                drv = i.parm('driver').eval()
                wd = hou.node(drv)
                rng = wd.parm('trange').eval()

                fstart = str(int(i.parm('range1x').eval()))
                fend = str(int(i.parm('range1y').eval()))
                fdur = str(int(i.parm('range1y').eval() - (i.parm('range1x').eval()-1)))               
                try: 
                    fstart = str(int(i.parm('wubs').eval()))
                    fend = str(int(i.parm('wube').eval()))
                    fdur = str(int(i.parm('wube').eval() - (i.parm('wubs').eval()-1)))
                except:
                    print("no wubs and wube parms, sending the whole thing...")
                i.parm('wrange').set(1)
                
                cc = int(fstart)
                for n in range(int(fdur)) :
                    i.parm('wedgenum').set(cc)
                    
                    n = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                    hup = os.path.dirname(hou.hipFile.name()) + '/' + 'delme_' + n + '.hip'
                    print(hup)
                    hou.hipFile.save()
                    cpycmd = "cp " + hou.hipFile.name() + " " + hup
                    print(cpycmd)
                    os.system(cpycmd)
                    
                    pcc = prepadstr(str(cc), "0", len(fdur)) 
                    batchcmd = pathtohoudini + "/bin/hbatch -c \"render -V " + opth + "\" -c  \"quit\" " +  hup
                    
                    if batchcmd != "" :
                        n = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                        print(batchcmd)
                        bsh = (hprj + '/farm/pending/' + n + '_' + pcc + '_' + hdir + '_' + hname + '_' + opn + '.sh')
                        if not os.path.exists(os.path.dirname(bsh)):
                            os.makedirs(os.path.dirname(bsh))
                        f = open(bsh,'w')
                        f.write(batchcmd + '\n')
                        f.close()
                    cc = cc + 1
                    print("cc="+str(cc))
                    time.sleep(2)]]