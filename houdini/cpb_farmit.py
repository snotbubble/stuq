# batch command generator by c.p.brown, 2018
# for encapsulated native projects
# hbatch only (I'm using Indie)
# linux only
# ...
# assumes farm is in /farm one level up from hip dir:
#     /path/to/project/shot/hip.hip
#     /path/to/project/farm/
#     /path/to/project/farm/pending/
#     /path/to/project/farm/running/
#     /path/to/project/farm/done/
#     /path/to/project/farm/themo.sh
# ...
# wedge is a messy bypass hack, hence the code bloat
# only mantra, geo and cop wedging will work atm
# wedge is farmed per frame, per wedge, unless its a sim
# adding int params 'wubs' and 'wube' to wedge will allow range override
# eg: render 5 to 8 of a 10-wedge setup
########################################################################

import os
import string
import getpass
import time
from datetime import datetime
from math import sqrt

usr = getpass.getuser()
pathtohoudini = "/opt/hfs" + hou.applicationVersionString()
ops = hou.selectedNodes()

# leading zeroes

def prepadstr(instr, pad, padlen) :
        dif = (padlen - len(instr)) + 1
        o = ''
        for i in range(1,dif) :
                o = o + pad
        o = o + instr
        #print(o)
        return(o)

# very slick get-factors function copied from stackexchange        
        
def factors(n):
    step = 2 if n%2 else 1
    return set(reduce(list.__add__,
        ([i, n/i] for i in range(1, int(sqrt(n))+1, step) if n % i == 0)))

        
        
if len(ops) >= 1 :

# get string vars for naming

    hscene = hou.hipFile.name()
    hname = hou.hipFile.path().split('.')[0].split('/')[-1]
    hdir = hou.hipFile.path().split('.')[0].split('/')[-3]
    hj = hou.hipFile.path().split('.')[0].split('/')[-2]
    hprj = "/".join(hou.hipFile.path().split('.')[0].split('/')[:-2])
    nx = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')

# save the scene  

    hup = os.path.dirname(hou.hipFile.name()) + '/' + 'delme_' + nx + '.hip'    
    hou.hipFile.save()
    cpycmd = "cp " + hou.hipFile.name() + " " + hup
    os.system(cpycmd)
   
# copy hfs to a farm-readable directory - yes this means it'll work with daily builds!  
    
    nethfs = hprj + "/farm/hfs/hfs" + hou.applicationVersionString()
    if not os.path.exists(nethfs):
        os.makedirs(nethfs)
        xcmd = ("rsync -av " + pathtohoudini + "/ " + nethfs + "/")
        os.system(xcmd)
    
# loop through selected ROPs    
    
    for i in ops :
        isasim = 1
        batchcmd = ""
        otn = i.type().name()
        if otn == 'rop_geometry' or otn == 'rop_dop' or otn == 'geometry' or otn == 'wedge' or otn == 'rop_comp' or otn == 'comp' or otn == 'ifd':
            opn = i.name()
            opth = i.path()
            print("selected rop " + opn + " is type " + otn)
            
# its a wedge

            if otn == 'wedge' :
                drv = i.parm('driver').eval()
                wd = hou.node(drv)
                wub = 0
                wisasim = 0      

# get wedge range, check if custom parms for start & end exist for rendering a subset                
                
                fstart = str(int(i.parm('range1x').eval()))
                fend = str(int(i.parm('range1y').eval()))
                fdur = str(int(i.parm('range1y').eval() - (i.parm('range1x').eval()-1)))
                try: 
                    fstart = str(int(i.parm('wubs').eval()))
                    fend = str(int(i.parm('wube').eval()))
                    fdur = str(int(i.parm('wube').eval() - (i.parm('wubs').eval()-1)))
                    wub = 1
                except:
                    print("\twedge has no wubs and wube parms, sending the whole thing...")
                    
# get wedge-driver range
                    
                rng = wd.parm('trange').eval()
                if rng == 0 :
                    sfstart = str(int(hou.frame()))
                    sfend = fstart
                    sfdur = "1"
                else :
                    sfstart = str(int(wd.parm('f1').eval()))
                    sfend = str(int(wd.parm('f2').eval()))
                    sfdur = str(int(wd.parm('f2').eval() - (wd.parm('f1').eval()-1)))                    

# is the wedge driver a sim?                    
                    
                try :
                    wisasim = wd.parm('initsim').eval()
                except:
                    wisasim = 0
 
# set wedge range to single_wedge
                    
                i.parm('wrange').set(1)
                
# get string vars from the wedge driver                
                
                wpth = wd.path()
                wpn = wd.name()
                oldfn = ""
                wtn = wd.type().name()
                print("\twedge driver " + wpn + " is type " + wtn)
                if wtn == 'ifd' : oldfn = wd.parm('vm_picture').eval()
                if wtn == 'geometry' : oldfn = wd.parm('sopoutput').eval()
                if wtn == 'rop_geometry' : oldfn = wd.parm('sopoutput').eval()
                if wtn == 'comp' : oldfn = wd.parm('copoutput').eval()
                if wtn == 'rop_comp' : oldfn = wd.parm('copoutput').eval()
                ext = oldfn.split(".")[-1]

# loop through the wedges                
                
                oldcc = 0
                cc = int(fstart)
                for n in range(int(fdur)) :
                    
# set wedge number:

                    i.parm('wedgenum').set(cc)

# is it a sim?
 
                    if not wisasim :

                        print("\t\twedge_" + str(cc) + " is not a sim, sending per-frame commands...")    
                    
# set per-wedge overrides, since setting wedgenum doesn't work we're just bypassing wedge altogether for non-sims:

                        ch = i.parm('chan1').eval()
                        oldcc = hou.parm(ch).eval()
                        hou.parm(ch).set(cc)
                        print("\t\t\tset channel " + ch + " to value: " + str(cc)) 
                        
# set wedge driver output manually as setting wedgenum doesn't work                
                
                        if wtn == 'ifd' : wd.parm('vm_picture').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4.pic")
                        if wtn == 'geometry' : wd.parm('sopoutput').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F.bgeo.sc")
                        if wtn == 'rop_geometry' : wd.parm('sopoutput').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F.bgeo.sc")
                        if wtn == 'comp' : wd.parm('copoutput').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4." + ext)
                        if wtn == 'rop_comp' : wd.parm('copoutput').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4." + ext)
                        if wtn == 'ifd' : print('\t\t\tchecking matra ROP filename: ' + wd.parm('vm_picture').eval())
                        
# save per-wedge hipfile:         

                        hou.hipFile.save()
                        whup = os.path.dirname(hou.hipFile.name()) + '/' + 'delme_' + nx + '_wedge_' + str(cc) + '.hip'
                        wcpycmd = "cp " + hou.hipFile.name() + " " + whup
                        os.system(wcpycmd)
                        print("\t\t\tsaved temp hipfile: " + whup)
                        
# get possible packet sizes, for future optimization for COPs

                        print("\t\t\tpacket sizes = " + str(factors(int(sfdur))))

# create batch scripts per frame for non-sims:
     
                        scc = int(sfstart)
                        for s in range(int(sfdur)) :
                            pcc = prepadstr(str(scc), "0", len(sfdur)) 
                            batchcmd = nethfs + "/bin/hbatch -c \"render -V -f" + str(scc) + " " + str(scc) + " " + wpth + "\" -c  \"quit\" " +  whup
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                #print(batchcmd)
                                bsh = (hprj + '/farm/pending/' + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + wpn + '_' + opn + '_wedge' + str(cc) + '.sh')
                                if not os.path.exists(os.path.dirname(bsh)):
                                    os.makedirs(os.path.dirname(bsh))
                                f = open(bsh,'w')
                                f.write(batchcmd + '\n')
                                f.close()
                            scc = scc + 1

# reset wedged channel value

                        hou.parm(ch).set(oldcc)

# reset the wedge driver file fields to my defaults
                    
                        if wtn == 'ifd' : wd.parm('vm_picture').set("$HIP/pic/${OS}/${OS}.$F4.pic")
                        if wtn == 'geometry' : wd.parm('sopoutput').set("$HIP/pic/${OS}/${OS}.$F.bgeo.sc")
                        if wtn == 'rop_geometry' : wd.parm('sopoutput').set("$HIP/pic/${OS}/${OS}.$F.bgeo.sc")
                        if wtn == 'comp' : wd.parm('copoutput').set("$HIP/pic/${OS}/${OS}.$F4." + ext)
                        if wtn == 'rop_comp' : wd.parm('copoutput').set("$HIP/pic/${OS}/${OS}.$F4." + ext)
                        print("\t\tper-frame commands sent")
                        
# create batch scripts for sims, no need to save hipfile per wedge as we're using the wedge ROP                           
                            
                    else:
                        print("wedge_" + str(cc) + " is a sim, sending as one command...")
                        for s in range(int(sfdur)) :
                            batchcmd = nethfs + "/bin/hbatch -c \"render -V " + wpth + "\" -c  \"quit\" " +  hup      
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                #print(batchcmd)
                                bsh = (hprj + '/farm/pending/' + nn + '_' + hdir + '_' + hj + '_' + hname + '_' + wpn + '_' + opn + '_wedge' + str(cc) + '.sh')
                                if not os.path.exists(os.path.dirname(bsh)):
                                    os.makedirs(os.path.dirname(bsh))
                                f = open(bsh,'w')
                                f.write(batchcmd + '\n')
                                f.close()
                                
# next wedge                                
                                
                    cc = cc + 1

# its not a wedge                
                
            else :
                 
# get ROP ranges

                rng = i.parm('trange').eval()
                if rng == 0 :
                    fstart = str(int(hou.frame()))
                    fend = fstart
                    fdur = "1"
                else :
                    fstart = str(int(i.parm('f1').eval()))
                    fend = str(int(i.parm('f2').eval()))
                    fdur = str(int(i.parm('f2').eval() - (i.parm('f1').eval()-1)))

# is it a sim?                    
                    
                try :
                    isasim = i.parm('initsim').eval()
                except:
                    isasim = 0
                    
# create batch scripts per frame if not a sim
                    
                cc = int(fstart)
                print("is a sim: " + str(isasim))
                if not isasim :
                    
                    if otn == 'comp' or 'rop_comp' :
                    
# do 10s for COPs, change dv to desired frames-per-job                  
                    
                        dv = 10
                        print('is a COP:')
                        cdur = int((int(fdur)) / float(dv))
                        print('\t'+str(dv)+'-frame job count = ' + str(cdur))
                        cdreg = (int(fdur))-(cdur*dv)
                        print('\tCOP range = ' + str(int(fdur)))
                        print('\tremainder = ' + str(cdreg))
                        print('\tsending '+str(dv)+'s...')
                        for n in range(cdur) :
                            cstart= (n*dv)+1
                            cend= (n*dv)+dv
                            print('\t\tjob ' + str(n) + ' start = ' + str(cstart) + ', end = '+str(cend))
                            pcc = prepadstr(str(cstart), "0", len(fdur)) 
                            batchcmd = nethfs + "/bin/hbatch -c \"render -V -f " + str(cstart) + " " + str(cend) + " " + opth + "\" -c  \"quit\" " +  hup
                            #print('\tcmd = ' + batchcmd)
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                bsh = (hprj + '/farm/pending/' + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
                                if not os.path.exists(os.path.dirname(bsh)):
                                    os.makedirs(os.path.dirname(bsh))
                                f = open(bsh,'w')
                                f.write(batchcmd + '\n')
                                f.close()
                        if cdreg > 0 :
                            print('\tsending dregs...')
                            cstart= (cdur*dv) + 1
                            cend= (int(fdur))
                            print('\t\tdregs start=' + str(cstart) + ', end = ' + str(cend))
                            pcc = prepadstr(str(cstart), "0", len(fdur)) 
                            batchcmd = nethfs + "/bin/hbatch -c \"render -V -f " + str(cstart) + " " + str(cend) + " " + opth + "\" -c  \"quit\" " +  hup
                            #print('\tcmd = ' + batchcmd)
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                bsh = (hprj + '/farm/pending/' + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
                                if not os.path.exists(os.path.dirname(bsh)):
                                    os.makedirs(os.path.dirname(bsh))
                                f = open(bsh,'w')
                                f.write(batchcmd + '\n')
                                f.close()                                
                            
                    else: 
                        for n in range(int(fdur)) :
                            pcc = prepadstr(str(cc), "0", len(fdur)) 
                            batchcmd = nethfs + "/bin/hbatch -c \"render -V -f" + str(cc) + " " + str(cc) + " " + opth + "\" -c  \"quit\" " +  hup
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                bsh = (hprj + '/farm/pending/' + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
                                if not os.path.exists(os.path.dirname(bsh)):
                                    os.makedirs(os.path.dirname(bsh))
                                f = open(bsh,'w')
                                f.write(batchcmd + '\n')
                                f.close()
                            cc = cc + 1
                        
# create batch script if sim                        
                        
                else:
                    batchcmd = nethfs + "/bin/hbatch -c \"render -V " + opth + "\" -c  \"quit\" " +  hup      
                    if batchcmd != "" :
                        nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                        #print(batchcmd)
                        bsh = (hprj + '/farm/pending/' + nn + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
                        if not os.path.exists(os.path.dirname(bsh)):
                            os.makedirs(os.path.dirname(bsh))
                        f = open(bsh,'w')
                        f.write(batchcmd + '\n')
                        f.close()