# farmit
simple Q

```
Batch command generator by c.p.brown, 2018
for encapsulated native projects
hbatch only (I'm using Indie)
Linux only

...

Assumes farm is in /farm TWO levels up from hip dir:
     /path/to/project/shot/task/hip.hip
     /path/to/project/farm/
     /path/to/project/farm/pending/
     /path/to/project/farm/running/
     /path/to/project/farm/done/
     
...
     
Usage:
 1. copy cpb_farmit.py to a new shelftool
 2. select some ROPs
 3. hit the button...

...
 
note:
 Doesn't do pause, resume, daisychaining, priorities or any other fancy things... 
 just executes a directory full of commands. While you sleep. 
 
 The shelftool will save your hipfile, then make a copy of it for the jobs to use.
 
 To get multiple machines on it just run themo.sh on the other computers (assuming they can see the farm dir).
 
 Composite rops are sent as 10s (cops too leaky to go higher).
 Compisite jobs may not successfully overwrite existing frames! I've reported this as a bug.  Work around it by deleting existing frames 1st.
 
 Wedge is a messy bypass hack, hence the code bloat
 only mantra, geo and cop wedging will work atm.
 Wedge is farmed per frame, per wedge, unless its a sim
 adding int params 'wubs' and 'wube' to wedge will allow range override
 eg: render 5 to 8 of a 10-wedge setup.

 Jobs are processed by date/time.
 To pull stuff off the queue just delete the job scripts from /farm/pending/
 Each machine will prefer scripts in a directory matching its name, eg: machine skullet will grab jobs from /farm/pending/skullet 1st.
 Whitelist by adding a 'whitelist' string parameter to the rop(s), separate machine names with spaces.

 Jobs can be monitored with thebeard.py
 Copy to /farm/ 
 Run in a terminal with watch -n 10 "python3 thebeard.py"
 Or call it every 10s with a monitoring applet
 
...
