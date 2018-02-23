# farmit
simple Q

```
Make a dir called farm in the project dir - one level up from $HIP,
add subdirs: pending, running, done and hfs,
copy themo.sh into it,
run themo.sh on all slaves.

Open Houdini,
copy contents of houdini scripts into respective shelf tools: 
farmit, wedge1b1, wedge1b1L,
select ROPs to render, hit the button for farmit on the shelf to farm the ROPS.

For wedge1by1local, make a farm on the desktop.

Tested OK on linux using computers networked with sshfs, just don't use the server for anything else.

Doesn't do pause, resume, daisychaining, priorities or any other fancy things... 
just executes a directory full of commands. While you sleep.
```
