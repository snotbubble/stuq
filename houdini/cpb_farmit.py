# batch command generator by c.p.brown, 2018
# for encapsulated native projects
# hbatch only (I'm using Indie)
# linux only
# ...
# assumes farm is in /farm TWO levels up from hip dir:
#     /path/to/project/shot/task/hip.hip
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

# change this to whatever is default on your distro
# don't use xterm as it locks-up houdini

myfaveterm = "xfce4-terminal"

# leading zeroes

def prepadstr(instr, pad, padlen) :
    dif = (padlen - len(instr)) + 1
    o = ''
    for i in range(1,dif) :
        o = o + pad
    o = o + instr
    #print(o)
    return(o)
    
    
if len(ops) >= 1 :

# get string vars for naming

    hscene = hou.hipFile.name()
    hname = hou.hipFile.path().split('.')[0].split('/')[-1].replace('_','-')
    hdir = hou.hipFile.path().split('.')[0].split('/')[-3].replace('_','-')
    hj = hou.hipFile.path().split('.')[0].split('/')[-2].replace('_','-')
    hprj = "/".join(hou.hipFile.path().split('.')[0].split('/')[:-3])
    nx = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
    
    print("\nthis project is : " + hprj)

# setup the farm

    pendingdir = hprj + "/farm/pending"
    runningdir = hprj + "/farm/running"
    donedir = hprj + "/farm/done"
    themofile = hprj + "/farm/themo.sh"

    if not os.path.exists(pendingdir): os.makedirs(pendingdir)
    if not os.path.exists(runningdir): os.makedirs(runningdir)
    if not os.path.exists(donedir): os.makedirs(donedir)
    
    if not os.path.exists(themofile) :
        themoscript = """#!/bin/sh
while true
do
        iam=`hostname -s`
        loc=`ls -1 ./pending/$iam/*.sh 2>/dev/null | wc -l`
        if [ $loc != 0 ]; then
            for file in ./pending/$iam/*.sh
                do
                    if [ -f $file ]; then
                        chmod u+x $file
                        src=$(readlink --canonicalize $file)
                        fnm=$(basename $src)
                        mkdir ./running/$iam/
                        mv $src ./running/$iam/$fnm
                        /bin/bash ./running/$iam/$fnm
                        mv ./running/$iam/$fnm ./done/$fnm
                        break
                    fi
            done
        else
            for file in ./pending/*.sh
                do
                    if [ -f $file ]; then
                        chmod u+x $file
                        src=$(readlink --canonicalize $file)
                        fnm=$(basename $src)
                        mkdir ./running/$iam/
                        mv $src ./running/$iam/$fnm
                        /bin/bash ./running/$iam/$fnm
                        mv ./running/$iam/$fnm ./done/$fnm
                        break
                    fi
                done
        fi
        file=0
        src=0
        fnm=0
        loc=0
        sleep 2
done
"""
        #print("themo.sh doesn't exist, writing it...\n" + themoscript + "\n")
        
# themo.sh doesn't exist...     

        f = open(themofile,"w")
        print("themo.sh doesn't exist, writing it...\n")
        for line in themoscript.splitlines():
            f.write(line + "\n")
        f.close()

# chmod themo.sh
        
        mode = os.stat(themofile).st_mode
        mode |= (mode & 0o444) >> 2 
        os.chmod(themofile, mode)

# run themo if not running already:
        
    #import subprocess
    #pids = subprocess.check_output(["ps","-efl", (hprj + "/farm/*" + themofile)])
    pids = -999
    
    # psutil not available...
    #import psutil
    #for proc in psutil.process_iter(): 
    #    cmds = " ".join(proc.cmds())
    #    if (hprj + "/farm/*themo.sh") in cmds :
    #        print("themo.sh is already running\n" + str(cmds))
    #        pids = 0
    #        break
    import subprocess
    ps = subprocess.Popen(['ps', 'efl'], stdout=subprocess.PIPE)
    pg = subprocess.Popen(['grep', 'themo.sh'], stdin=ps.stdout, stdout=subprocess.PIPE).communicate()[0]
    ps.stdout.close() 
    if pg.strip() != ""  : pids = 1
    pg = 0
    ps = 0
    if pids == 1 :
        print("themo.sh is already running...")
    else :
        print("themo not running, starting it...")
        os.system(myfaveterm + " -e 'bash -c \"cd " + hprj + "/farm/; ./themo.sh\"'")
    
# save the scene  

    hup = os.path.dirname(hou.hipFile.name()) + '/' + 'delme_' + nx + '.hip'    
    hou.hipFile.save()
    cpycmd = "cp " + hou.hipFile.name() + " " + hup
    print("making a temp file for this job : " + cpycmd)
    os.system(cpycmd)
   
# copy hfs to a farm-readable directory - yes this means it'll work with daily builds!  
    
    nethfs = hprj + "/farm/hfs/hfs" + hou.applicationVersionString()
    if not os.path.exists(nethfs):
        os.makedirs(nethfs)
    if not os.path.exists(nethfs):
        print("ERROR: couldn't create nethfs dir : " + nethfs)
    else:
        xcmd = ("rsync -av " + pathtohoudini + "/ " + nethfs + "/")
        print("sync hfs : " + xcmd)
        os.system(xcmd)
    
# loop through selected ROPs    
    
    for i in ops :
        isasim = 1
        fto = ''
        batchcmd = ""
        otn = i.type().name()
        if otn == 'rop_geometry' or otn == 'rop_dop' or otn == 'geometry' or otn == 'wedge' or otn == 'rop_comp' or otn == 'comp' or otn == 'ifd' or otn == 'opengl' :
            opn = i.name()
            opth = i.path()
            print("selected rop " + opn + " is type " + otn)
            
# does it have a host filter? set paths to use it

            try :
                fto = i.parm('whitelist').eval() + '/'
            except :
                fto = ''
            if fto == '/' : fto = ''

# its a wedge

            if otn == 'wedge' :
                drv = i.parm('driver').eval()
                wd = hou.node(drv)
                wub = 0
                wisasim = 0      

# get wedge range, check if custom parms for start & end exist for rendering a subset                
                
                fstart = 0
                fvstart = str(int(i.parm('range1x').eval()))
                fend = str(int(i.parm('steps1').eval())-1)
                fvend = str(int(i.parm('range1y').eval())-1)
                fvdur = str(int(i.parm('range1y').eval() - (i.parm('range1x').eval()-1)))
                fdur = str(int(i.parm('steps1').eval()))
                try: 
                    fvstart = str(int(i.parm('wubs').eval()))
                    fvend = str(int(i.parm('wube').eval()))
                    fvdur = str(int(i.parm('wube').eval() - (i.parm('wubs').eval()-1)))
                    fend = str(int(i.parm('steps1').eval())-1)
                    fdur = str(int(i.parm('steps1').eval()))
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
                wisasim = 0
                
                try :
                    wisasim = wd.parm('initsim').eval()
                except:
                    print("wedge driver isn't a sim")
                    
                if wd.type().name() == 'opengl' :
                    try :
                        wisasim = wd.parm('soho_initsim').eval()
                    except:
                        print("wedge OGL driver isn't a sim")
                    
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
                if wtn == 'opengl' : oldfn = wd.parm('picture').eval()
                ext = oldfn.split(".")[-1]

# loop through the wedges                
                
                oldcc = 0
                cc = int(fstart)
                for n in range(int(fdur)) :
                    wv = (n/((int(fdur)-1) * 1.0)) * (int(fvdur) * 1.0)
                                    
# set wedge range to single_wedge
                
                    i.parm('wrange').set(1)
                
# set wedge number:
                
                    i.parm('wedgenum').set(cc)
                
# set per-wedge overrides, since setting wedgenum doesn't work we're just bypassing wedge altogether for non-sims:

                    ch = i.parm('chan1').eval()
                    oldcc = hou.parm(ch).eval()
                    hou.parm(ch).set(wv)
                    print("\t\t\tset channel " + ch + " to value: " + str(wv)) 
                    
# set wedge driver output manually as there is no wedgeval yet                
            
                    if wtn == 'ifd' : wd.parm('vm_picture').set("$HIP/ifd/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4.pic")
                    if wtn == 'geometry' : wd.parm('sopoutput').set("$HIP/tmp/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F.bgeo.sc")
                    if wtn == 'rop_geometry' : wd.parm('sopoutput').set("$HIP/tmp/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F.bgeo.sc")
                    if wtn == 'comp' : wd.parm('copoutput').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4." + ext)
                    if wtn == 'rop_comp' : wd.parm('copoutput').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4." + ext)
                    if wtn == 'opengl' : wd.parm('picture').set("$HIP/pic/${OS}_" + str(cc) + "/${OS}_" + str(cc) + ".$F4." + ext)
                    if wtn == 'ifd' : print('\t\t\tchecking matra ROP filename: ' + wd.parm('vm_picture').eval())
                    
# save per-wedge hipfile:         

                    hou.hipFile.save()
                    whup = os.path.dirname(hou.hipFile.name()) + '/' + 'delme_' + nx + '_wedge_' + str(cc) + '.hip'
                    wcpycmd = "cp " + hou.hipFile.name() + " " + whup
                    os.system(wcpycmd)
                    print("\t\t\tsaved temp hipfile: " + whup)

# create batch scripts per frame for non-sims:

                    if not wisasim :
                        print("\t\t\twedge_" + str(cc) + " is not a sim, sending per-frame commands...")   
                        scc = int(sfstart)
                        for s in range(int(sfdur)) :
                            pcc = prepadstr(str(scc), "0", len(sfdur)) 
                            batchcmd = nethfs + "/bin/hbatch -c \"render -V -f" + str(scc) + " " + str(scc) + " " + wpth + "\" -c  \"quit\" " +  whup
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                #print(batchcmd)
                                bsh = (hprj + '/farm/pending/' + fto + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + wpn + '_' + opn + '_wedge' + str(cc) + '.sh')
                                #print(bsh)
                                if not os.path.exists(os.path.dirname(bsh)):
                                    os.makedirs(os.path.dirname(bsh))
                                f = open(bsh,'w')
                                f.write(batchcmd + '\n')
                                f.close()
                            scc = scc + 1
                    else:
                    
# driver is a sim, send one job per wedge only:                    
                        print("\t\t\tis a sim, sending one job per wedge")
                        batchcmd = nethfs + "/bin/hbatch -c \"render -V " + wpth + "\" -c  \"quit\" " +  whup
                        if batchcmd != "" :
                            nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                            print("\t\t\t" + batchcmd)
                            bsh = (hprj + '/farm/pending/' + fto + nn + '_' + hdir + '_' + hj + '_' + hname + '_' + wpn + '_' + opn + '_wedge' + str(cc) + '.sh')
                            print("\t\t\t" + bsh)
                            if not os.path.exists(os.path.dirname(bsh)):
                                os.makedirs(os.path.dirname(bsh))
                            f = open(bsh,'w')
                            f.write(batchcmd + '\n')
                            f.close()                
                    

# reset wedged channel value

                        hou.parm(ch).set(oldcc)
                                                                                
# next wedge                                
                                
                    cc = cc + 1

# reset wedge range mode

                    i.parm('wrange').set(0)

# reset the wedge driver file fields to my defaults
                    
                    if wtn == 'ifd' : wd.parm('vm_picture').set("$HIP/ifd/${WEDGENUM}_${OS}/${WEDGENUM}_${OS}.$F4.pic")
                    if wtn == 'geometry' : wd.parm('sopoutput').set("$HIP/tmp/${WEDGENUM}_${OS}/${WEDGENUM}_${OS}.$F.bgeo.sc")
                    if wtn == 'rop_geometry' : wd.parm('sopoutput').set("$HIP/tmp/${WEDGENUM}_${OS}/${WEDGENUM}_${OS}.$F.bgeo.sc")
                    if wtn == 'comp' : wd.parm('copoutput').set("$HIP/pic/${WEDGENUM}_${OS}/${WEDGENUM}_${OS}.$F4." + ext)
                    if wtn == 'rop_comp' : wd.parm('copoutput').set("$HIP/pic/${WEDGENUM}_${OS}/${WEDGENUM}_${OS}.$F4." + ext)
                    if wtn == 'opengl' : wd.parm('picture').set("$HIP/pic/${WEDGENUM}_${OS}/${WEDGENUM}_${OS}.$F4." + ext)
                    
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
                    
                    if otn == 'comp' or otn == 'rop_comp' :
                    
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
                            print('\tcmd = ' + batchcmd)
                            if batchcmd != "" :
                                nn = datetime.strftime(datetime.now(),'%y%m%d_%H%M%S')
                                bsh = (hprj + '/farm/pending/' + fto + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
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
                                bsh = (hprj + '/farm/pending/' + fto + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
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
                                bsh = (hprj + '/farm/pending/' + fto + nn + '_' + pcc + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
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
                        bsh = (hprj + '/farm/pending/' + fto + nn + '_' + hdir + '_' + hj + '_' + hname + '_' + opn + '.sh')
                        if not os.path.exists(os.path.dirname(bsh)):
                            os.makedirs(os.path.dirname(bsh))
                        f = open(bsh,'w')
                        f.write(batchcmd + '\n')
                        f.close()
