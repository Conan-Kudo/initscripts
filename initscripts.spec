Summary: The inittab file and the /etc/rc.d scripts.
Name: initscripts
%define version 4.72
Version: %{version}
Copyright: GPL
Group: System Environment/Base
Release: 1
Source: initscripts-%{version}.tar.gz
BuildRoot: /%{_tmppath}/%{name}-%{version}-%{release}-root
Requires: mingetty, /bin/awk, /bin/sed, mktemp, e2fsprogs >= 1.15, console-tools
Requires: procps, modutils >= 2.1.121, sysklogd >= 1.3.31
Requires: setup >= 2.0.3, /sbin/fuser
%ifarch alpha
Requires: util-linux >= 2.9w-26
%endif
Conflicts: kernel <= 2.2, timeconfig < 3.0, pppd < 2.3.9, wvdial < 1.40-3
Conflicts: initscripts < 1.22.1-5
Obsoletes: rhsound
Prereq: /sbin/chkconfig, /usr/sbin/groupadd, gawk

%description
The initscripts package contains the basic system scripts used to boot
your Red Hat system, change run levels, and shut the system down
cleanly.  Initscripts also contains the scripts that activate and
deactivate most network interfaces.

%prep
%setup -q

%build
make CFLAGS="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc
make ROOT=$RPM_BUILD_ROOT install 
mkdir -p $RPM_BUILD_ROOT/var/run/netreport
#chown root.root $RPM_BUILD_ROOT/var/run/netreport
chmod u=rwx,g=rwx,o=rx $RPM_BUILD_ROOT/var/run/netreport

for i in 0 1 2 3 4 5 6 ; do
  file=$RPM_BUILD_ROOT/etc/rc.d/rc$i.d
  mkdir $file
# chown root.root $file
  chmod u=rwx,g=rx,o=rx $file
done

# Can't store symlinks in a CVS archive
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K80random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc1.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc4.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S20random
ln -s ../init.d/random $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K80random

ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K75netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc1.d/K75netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc2.d/K75netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S25netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc4.d/S25netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S25netfs
ln -s ../init.d/netfs $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K75netfs

ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K90network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc1.d/K90network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc4.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S10network
ln -s ../init.d/network $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K90network

ln -s ../init.d/killall $RPM_BUILD_ROOT/etc/rc.d/rc0.d/S00killall
ln -s ../init.d/killall $RPM_BUILD_ROOT/etc/rc.d/rc6.d/S00killall

ln -s ../init.d/halt $RPM_BUILD_ROOT/etc/rc.d/rc0.d/S01halt
ln -s ../init.d/halt $RPM_BUILD_ROOT/etc/rc.d/rc6.d/S01reboot

ln -s ../init.d/single $RPM_BUILD_ROOT/etc/rc.d/rc1.d/S00single

ln -s ../rc.local $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S99local
ln -s ../rc.local $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S99local
ln -s ../rc.local $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S99local

mkdir -p $RPM_BUILD_ROOT/var/{log,run}
touch $RPM_BUILD_ROOT/var/run/utmp
touch $RPM_BUILD_ROOT/var/log/wtmp


%pre
/usr/sbin/groupadd -g 22 -r -f utmp

%post
touch /var/log/wtmp
touch /var/run/utmp
chown root.utmp /var/log/wtmp /var/run/utmp
chmod 664 /var/log/wtmp /var/run/utmp

chkconfig --add random 
chkconfig --add netfs 
chkconfig --add network 

# handle serial installs semi gracefully
if [ $1 = 0 ]; then
  if [ "$TERM" = "vt100" ]; then
      tmpfile=/etc/sysconfig/tmp.$$
      sed -e '/BOOTUP=color/BOOTUP=serial/' /etc/sysconfig/init > $tmpfile
      mv -f $tmpfile /etc/sysconfig/init
  fi
fi

# dup of timeconfig %post - here to avoid a dependency
if [ -L /etc/localtime ]; then
    _FNAME=`ls -ld /etc/localtime | awk '{ print $11}' | sed 's/lib/share/'`
    rm /etc/localtime
    cp -f $_FNAME /etc/localtime
    if ! grep -q "^ZONE=" /etc/sysconfig/clock ; then
      echo "ZONE=\"$_FNAME"\" | sed -e "s|[^\"]*/usr/share/zoneinfo/||" >> /etc/sysconfig/clock
    fi
fi

%preun
if [ $1 = 0 ]; then
  chkconfig --del random
  chkconfig --del netfs
  chkconfig --del network
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%dir /etc/sysconfig/network-scripts
%config %verify(not md5 mtime size) /etc/adjtime
%config(noreplace) /etc/sysconfig/init
/etc/sysconfig/network-scripts/ifdown
%config /sbin/ifdown
%config /etc/sysconfig/network-scripts/ifdown-post
/etc/sysconfig/network-scripts/ifup
%config /sbin/ifup
%dir /etc/sysconfig/console
%config /etc/sysconfig/network-scripts/network-functions
%config /etc/sysconfig/network-scripts/ifup-post
%config /etc/sysconfig/network-scripts/ifcfg-lo
%config /etc/sysconfig/network-scripts/ifdown-ppp
%config /etc/sysconfig/network-scripts/ifdown-sl
%config /etc/sysconfig/network-scripts/ifup-ppp
%config /etc/sysconfig/network-scripts/ifup-sl
%config /etc/sysconfig/network-scripts/ifup-routes
%config /etc/sysconfig/network-scripts/ifup-plip
%config /etc/sysconfig/network-scripts/ifup-aliases
%config /etc/sysconfig/network-scripts/ifup-ipx
%config /etc/X11/prefdm
%config /etc/inittab
%dir    /etc/rc.d
%config /etc/rc.d/rc.sysinit
%dir    /etc/rc.d/rc0.d
%config(missingok) /etc/rc.d/rc0.d/*
%dir    /etc/rc.d/rc1.d
%config(missingok) /etc/rc.d/rc1.d/*
%dir    /etc/rc.d/rc2.d
%config(missingok) /etc/rc.d/rc2.d/*
%dir    /etc/rc.d/rc3.d
%config(missingok) /etc/rc.d/rc3.d/*
%dir    /etc/rc.d/rc4.d
%config(missingok) /etc/rc.d/rc4.d/*
%dir    /etc/rc.d/rc5.d
%config(missingok) /etc/rc.d/rc5.d/*
%dir    /etc/rc.d/rc6.d
%config(missingok) /etc/rc.d/rc6.d/*
%dir    /etc/rc.d/init.d
%config(missingok) /etc/rc.d/init.d/*
%config /etc/rc.d/rc
%config(noreplace) /etc/rc.d/rc.local
%config /etc/profile.d/lang.sh
%config /etc/profile.d/lang.csh
/usr/sbin/sys-unconfig
/sbin/setsysfont
/bin/doexec
/bin/ipcalc
/bin/usleep
%attr(4755,root,root) /usr/sbin/usernetctl
/sbin/consoletype
/sbin/getkey
%attr(2755,root,root) /sbin/netreport
/sbin/initlog
/sbin/minilogd
/sbin/service
/sbin/ppp-watch
/usr/man/man*/*
%dir %attr(775,root,root) /var/run/netreport
%config /etc/ppp/ip-up
%config /etc/ppp/ip-down
%config /etc/initlog.conf
%doc sysconfig.txt sysvinitfiles
%ghost %attr(0664,root,utmp) /var/log/wtmp
%ghost %attr(0664,root,utmp) /var/run/utmp

%changelog
* Mon Dec 13 1999 Bill Nottingham <notting@redhat.com>
- umount /proc *after* trying to turn off raid

* Mon Dec 06 1999 Michael K. Johnson <johnsonm@redhat.com>
- improvements in clone device handling
- better signal handling in ppp-watch
- yet another attempt to fix those rare PAP/CHAP problems

* Sat Nov 28 1999 Bill Nottingham <notting@redhat.com>
- impressive. Three new features, three new bugs.

* Mon Nov 22 1999 Michael K. Johnson <johnsonm@redhat.com>
- fix more possible failed CHAP authentication (with chat scripts)
- fix ppp default route problem
- added ppp-watch man page, fixed usernetctl man page
- make ifup-ppp work again when called from netcfg and linuxconf
- try to keep ppp-watch from filling up logs by respawning pppd too fast
- handle all linuxconf-style alias files with linuxconf

* Mon Nov 22 1999 Bill Nottingham <notting@redhat.com>
- load mixer settings for monolithic sound
- man page for ppp-watch
- add ARP variable for ifup
- some i18n fixes

* Wed Nov 10 1999 Bill Nottingham <notting@redhat.com>
- control stop-a separately from sysrq

* Mon Nov 08 1999 Michael K. Johnson <johnsonm@redhat.com>
- fix some failed CHAP authentication
- fix extremely unlikely, but slightly possible kill-random-process
  bug in ppp-watch
- allow DNS{1,2} in any ifcfg-* file, not just PPP, and
  add nameserver entries, don't just replace them
- don't use /tmp/confirm, use /var/run/confirm instead

* Tue Nov  2 1999 Bill Nottingham <notting@redhat.com>
- fix lang.csh /tmp race oops

* Wed Oct 27 1999 Bill Nottingham <notting@redhat.com>
- we now ship hwclock on alpha.

* Mon Oct 25 1999 Jakub Jelinek <jakub@redhat.com>
- fix check for serial console, don't use -C argument to fsck
  on serial console.

* Mon Oct 18 1999 Bill Nottingham <notting@redhat.com>
- do something useful with linuxconf 'any' static routes.

* Tue Oct 12 1999 Matt Wilson <msw@redhat.com>
- added patch from Owen to source i18n configuration before starting prefdm

* Mon Oct 11 1999 Bill Nottingham <notting@redhat.com>
- support for linuxconf alias files
- add support for Jensen clocks.

* Tue Oct  5 1999 Bill Nottingham <notting@redhat.com>
- assorted brown paper bag fixes
- check for programs/files before executing/sourcing them
- control stop-a like magic sysrq

* Thu Sep 30 1999 Bill Nottingham <notting@redhat.com>
- req. e2fsprogs >= 1.15

* Fri Sep 24 1999 Bill Nottingham <notting@redhat.com>
- munge C locale definitions to en_US
- use fsck's completion bar

* Thu Sep 23 1999 Michael K. Johnson <johnsonm@redhat.com>
- ppp-watch now always kills pppd pgrp to make sure dialers are dead,
  and tries to hang up the modem

* Tue Sep 21 1999 Bill Nottingham <notting@redhat.com>
- add a DEFRAG_IPV4 option

* Mon Sep 20 1999 Michael K. Johnson <johnsonm@redhat.com>
- changed to more modern defaults for PPP connections

* Mon Sep 20 1999 Bill Nottingham <notting@redhat.com>
- kill processes for umount in halt, too.
- fixes to remove /usr dependencies

* Fri Sep 17 1999 Bill Nottingham <notting@redhat.com>
- load/save mixer settings in rc.sysinit, halt

* Mon Sep 13 1999 Michael K. Johnson <johnsonm@redhat.com>
- add --remotename option to wvdial code
- make sure we do not have an earlier version of wvdial that doesn't
  know how handle --remotename
- make ppp-watch background itself after 30 seconds even if
  connection does not come up, at boot time only, so that a
  non-functional PPP connection cannot hang boot.

* Sun Sep 12 1999 Bill Nottingham <notting@redhat.com>
- a couple of /bin/sh -> /bin/bash fixes
- fix swapoff silliness

* Fri Sep 10 1999 Bill Nottingham <notting@redhat.com>
- chkconfig --del in %preun, not %postun
- use killall5 in halt
- swapoff non-/etc/fstab swap

* Wed Sep 08 1999 Michael K. Johnson <johnsonm@redhat.com>
- ifdown now synchronous (modulo timeouts)
- several unrelated cleanups, primarily in ifdown

* Tue Sep  7 1999 Bill Nottingham <notting@redhat.com>
- add an 'unconfigure' sort of thing

* Mon Sep 06 1999 Michael K. Johnson <johnsonm@redhat.com>
- added ppp-watch to make "ifup ppp*" synchronous

* Fri Sep  3 1999 Bill Nottingham <notting@redhat.com>
- require lsof

* Wed Sep  1 1999 Bill Nottingham <notting@redhat.com>
- add interactive prompt

* Tue Aug 31 1999 Bill Nottingham <notting@redhat.com>
- disable magic sysrq by default

* Mon Aug 30 1999 Bill Nottingham <notting@redhat.com>
- new NFS unmounting from Bill Rugolsky <rugolsky@ead.dsa.com> 
- fix ifup-sl/dip confusion
- more raid startup cleanup
- make utmp group 22

* Fri Aug 20 1999 Bill Nottingham <notting@redhat.com>
- pass hostname to pump
- add lang.csh

* Thu Aug 19 1999 Bill Nottingham <notting@redhat.com>
- more wvdial updates
- fix a *stupid* bug in process reading

* Fri Aug 13 1999 Bill Nottingham <notting@redhat.com>
- add new /boot/kernel.h boot kernel version file
- new RAID startup

* Fri Aug 13 1999 Michael K. Johnson <johnsonm@redhat.com>
- use new linkname argument to pppd to make if{up,down}-ppp
  reliable -- requires ppp-2.3.9 or higher

* Mon Aug  2 1999 Bill Nottingham <notting@redhat.com>
- fix typo.
- add 'make check'

* Wed Jul 28 1999 Michael K. Johnson <johnsonm@redhat.com>
- simple wvdial support for ppp connections

* Mon Jul 26 1999 Bill Nottingham <notting@redhat.com>
- stability fixes for initlog
- initlog now has a config file
- add alias speedup from dharris@drh.net
- move netfs links
- usleep updates

* Thu Jul  8 1999 Bill Nottingham <notting@redhat.com>
- remove timeconfig dependency
- i18n fixes from nkbj@image.dk
- move inputrc to setup package

* Tue Jul  6 1999 Bill Nottingham <notting@redhat.com>
- fix killall links, some syntax errors

* Fri Jun 25 1999 Bill Nottingham <notting@redhat.com>
- don't make module-info, System.map links
- handle utmpx/wtmpx
- fix lots of bugs in 4.21 release :)

* Thu Jun 17 1999 Bill Nottingham <notting@redhat.com>
- set clock as soon as possible
- use INITLOG_ARGS everywhere
- other random fixes in networking

* Mon Jun 14 1999 Bill Nottingham <notting@redhat.com>
- oops, don't create /var/run/utmp and then remove it.
- stomp RAID bugs flat. Sort of.

* Mon May 24 1999 Bill Nottingham <notting@redhat.com>
- clean out /var better
- let everyone read /var/run/ppp*.dev
- fix network startup so it doesn't depend on /usr

* Tue May 11 1999 Bill Nottingham <notting@redhat.com>
- various fixes to rc.sysinit
- fix raid startup
- allow for multi-processor /etc/issues

* Sun Apr 18 1999 Matt Wilson <msw@redhat.com>
- fixed typo - "Determing" to "Determining"

* Fri Apr 16 1999 Preston Brown <pbrown@redhat.com>
- updated inputrc so that home/end/del work on console, not just X

* Thu Apr 08 1999 Bill Nottingham <notting@redhat.com>
- fix more logic in initlog
- fix for kernel versions in ifup-aliases
- log to /var/log/boot.log

* Wed Apr 07 1999 Bill Nottingham <notting@redhat.com>
- fix daemon() function so you can specify pid to look for

* Wed Apr 07 1999 Erik Troan <ewt@redhat.com>
- changed utmp,wtmp to be group writeable and owned by group utmp

* Tue Apr 06 1999 Bill Nottingham <notting@redhat.com>
- fix loading of consolefonts/keymaps
- three changelogs. three developers. one day. Woohoo!

* Tue Apr 06 1999 Michael K. Johnson <johnsonm@redhat.com>
- fixed ifup-ipx mix-up over . and _

* Tue Apr 06 1999 Erik Troan <ewt@redhat.com>
- run /sbin/ifup-local after bringing up an interface (if that file exists)

* Mon Apr  5 1999 Bill Nottingham <notting@redhat.com>
- load keymaps & console font early
- fixes for channel bonding, strange messages with non-boot network interfaces

* Sat Mar 27 1999 Cristian Gafton <gafton@redhat.com>
- added sysvinitfiles as a documenattaion file

* Fri Mar 26 1999 Bill Nottingham <notting@redhat.com>
- nfsfs -> netfs

* Mon Mar 22 1999 Bill Nottingham <notting@redhat.com>
- don't source /etc/sysconfig/init if $BOOTUP is already set

* Fri Mar 19 1999 Bill Nottingham <notting@redhat.com>
- don't run linuxconf if /usr isn't mounted
- set macaddr before bootp
- zero in the /var/run/utmpx file (gafton)
- don't set hostname on ppp/slip (kills X)
			
* Wed Mar 17 1999 Bill Nottingham <notting@redhat.com>
- exit ifup if pump fails
- fix stupid errors in reading commands from subprocess

* Tue Mar 16 1999 Bill Nottingham <notting@redhat.com>
- fix ROFS logging
- make fsck produce more happy output
- fix killproc logic

* Mon Mar 15 1999 Bill Nottingham <notting@redhat.com>
- doc updates
- support for SYSFONTACM, other console-tools stuff
- add net route for interface if it isn't there.
- fix for a bash/bash2 issue

* Mon Mar 15 1999 Michael K. Johnson <johnsonm@redhat.com>
- pam_console lockfile cleanup added to rc.sysinit

* Sun Mar 14 1999 Bill Nottingham <notting@redhat.com>
- fixes in functions for 'action'
- fixes for pump

* Wed Mar 10 1999 Bill Nottingham <notting@redhat.com>
- Mmm. Must always remove debugging code. before release. *thwap*
- pump support
- mount -a after mount -a -t nfs

* Thu Feb 25 1999 Bill Nottingham <notting@redhat.com>
- put preferred support back in

* Thu Feb 18 1999 Bill Nottingham <notting@redhat.com>
- fix single-user mode (source functions, close if)

* Wed Feb 10 1999 Bill Nottingham <notting@redhat.com>
- turn off xdm in runlevel 5 (now a separate service)

* Thu Feb  4 1999 Bill Nottingham <notting@redhat.com>
- bugfixes (ifup-ppp, kill -TERM, force fsck, hwclock --adjust, setsysfont)
- add initlog support. Now everything is logged (and bootup looks different)

* Thu Nov 12 1998 Preston Brown <pbrown@redhat.com>
- halt now passed the '-i' flag so that network interfaces disabled

* Tue Nov 10 1998 Michael K. Johnson <johnsonm@redhat.com>
- handle new linuxconf output for ipaliases

* Mon Oct 15 1998 Erik Troan <ewt@redhat.com>
- fixed raid start stuff
- added raidstop to halt

* Mon Oct 12 1998 Cristian Gafton <gafton@redhat.com>
- handle LC_ALL

* Mon Oct 12 1998 Preston Brown <pbrown@redhat.com>
- adjusted setsysfont to always run setfont, even if only w/default font

* Tue Oct 06 1998 Cristian Gafton <gafton@redhat.com>
- rc.sysvinit should be working with all kernel versions now
- requires e2fsprogs (for fsck)
- set INPUTRC and LESSCHARSET on linux-lat

* Wed Sep 16 1998 Jeff Johnson <jbj@redhat.com>
- /etc/rc.d/rc: don't run /etc/rc.d/rcN.d/[KS]??foo.{rpmsave,rpmorig} scripts.
- /etc/rc.d/rc.sysinit: raid startup (Nigel.Metheringham@theplanet.net).
- /sbin/setsysfont: permit unicode fonts.

* Mon Aug 17 1998 Erik Troan <ewt@redhat.com>
- don't add 'Red Hat Linux' to /etc/issue; use /etc/redhat-release as is

* Sun Aug 16 1998 Jeff Johnson <jbj@redhat.com>
- paranoia improvements to .rhkmvtag
- if psacct with /sbin/accton, than turn off accounting

* Tue Jul  7 1998 Jeff Johnson <jbj@redhat.com>
- start/stop run levels changed.
- ipx_configure/ipx_internal_net moved to /sbin.

* Wed Jul 01 1998 Erik Troan <ewt@redhat.com>
- usernetctl didn't understand "" around USERCTL attribute

* Wed Jul  1 1998 Jeff Johnson <jbj@redhat.com>
- Use /proc/version to find preferred modules.
- Numerous buglets fixed.

* Sun Jun 07 1998 Erik Troan <ewt@redhat.com> 
- rc.sysinit looks for bootfile= as well as BOOT_IMAGE to set 
  /lib/modules/preferred symlink

* Mon Jun 01 1998 Erik Troan <ewt@redhat.com>
- ipcalc should *never* have been setgid anything
- depmod isn't run properly for non-serial numbered kernels

* Wed May 06 1998 Donnie Barnes <djb@redhat.com>
- added system font and language setting

* Mon May 04 1998 Michael K. Johnson <johnsonm@redhat.com>
- Added missing files to packagelist.

* Sat May 02 1998 Michael K. Johnson <johnsonm@redhat.com>
- Added lots of linuxconf support.  Should still work on systems that
  do not have linuxconf installed, but linuxconf gives enhanced support.
- In concert with linuxconf, added IPX support.  Updated docs to reflect it.

* Fri May 01 1998 Erik Troan <ewt@redhat.com>
- rc.sysinit uses preferred directory

* Sun Apr 05 1998 Erik Troan <ewt@redhat.com>
- updated rc.sysinit to deal with kernel versions with release numbers

* Sun Mar 22 1998 Erik Troan <ewt@redhat.com>
- use ipcalc to calculate the netmask if one isn't specified

* Tue Mar 10 1998 Erik Troan <ewt@redhat.com>
- added and made use of ipcalc

* Tue Mar 10 1998 Erik Troan <ewt@redhat.com>
- removed unnecessary dhcp log from /tmp

* Mon Mar 09 1998 Erik Troan <ewt@redhat.com>
- if bootpc fails, take down the device

* Mon Mar 09 1998 Erik Troan <ewt@redhat.com>
- added check for mktemp failure

* Thu Feb 05 1998 Erik Troan <ewt@redhat.com>
- fixed support for user manageable cloned devices

* Mon Jan 12 1998 Michael K. Johnson <johnsonm@redhat.com>
- /sbin/ isn't always in $PATH, so call /sbin/route in ifup-routes

* Wed Dec 31 1997 Erik Troan <ewt@redhat.com>
- touch /var/lock/subsys/kerneld after cleaning out /var/lock/subsys
- the logic for when  /var/lock/subsys/kerneld is touched was backwards

* Tue Dec 30 1997 Erik Troan <ewt@redhat.com>
- tried to get /proc stuff right one more time (uses -t nonfs,proc now)
- added support for /fsckoptions
- changed 'yse' to 'yes' in KERNELD= line

* Tue Dec 09 1997 Erik Troan <ewt@redhat.com>
- set domainname to "" if none is specified in /etc/sysconfig/network
- fix /proc mounting to get it in /etc/mtab

* Mon Dec 08 1997 Michael K. Johnson <johnsonm@redhat.com>
- fixed inheritance for clone devices

* Fri Nov 07 1997 Erik Troan <ewt@redhat.com>
- added sound support to rc.sysinit

* Fri Nov 07 1997 Michael K. Johnson <johnsonm@redhat.com>
- Added missing "then" clause

* Thu Nov 06 1997 Michael K. Johnson <johnsonm@redhat.com>
- Fixed DEBUG option in ifup-ppp
- Fixed PPP persistance
- Only change IP forwarding if necessary

* Tue Oct 28 1997 Donnie Barnes <djb@redhat.com>
- removed the skeleton init script
- added the ability to 'nice' daemons

* Tue Oct 28 1997 Erik Troan <ewt@redhat.com>
- touch /var/lock/subsys/kerneld if it's running, and after mounting /var
- applied dhcp fix

* Thu Oct 23 1997 Donnie Barnes <djb@redhat.com>
- added status|restart to init scripts

* Thu Oct 23 1997 Michael K. Johnson <johnsonm@redhat.com>
- touch random seed file before chmod'ing it.

* Wed Oct 15 1997 Erik Troan <ewt@redhat.com>
- run domainname if NISDOMAIN is set 

* Wed Oct 15 1997 Michael K. Johnson <johnsonm@redhat.com>
- Make the random seed file mode 600.

* Tue Oct 14 1997 Michael K. Johnson <johnsonm@redhat.com>
- bring down ppp devices if ifdown-ppp is called while ifup-ppp is sleeping.

* Mon Oct 13 1997 Erik Troan <ewt@redhat.com>
- moved to new chkconfig conventions

* Sat Oct 11 1997 Erik Troan <ewt@redhat.com>
- fixed rc.sysinit for hwclock compatibility

* Thu Oct 09 1997 Erik Troan <ewt@redhat.com>
- run 'ulimit -c 0' before running scripts in daemon function

* Wed Oct 08 1997 Donnie Barnes <djb@redhat.com>
- added chkconfig support
- made all rc*.d symlinks have missingok flag

* Mon Oct 06 1997 Erik Troan <ewt@redhat.com>
- fixed network-scripts to allow full pathnames as config files
- removed some old 3.0.3 pcmcia device handling

* Wed Oct 01 1997 Michael K. Johnson <johnsonm@redhat.com>
- /var/run/netreport needs to be group-writable now that /sbin/netreport
  is setguid instead of setuid.

* Tue Sep 30 1997 Michael K. Johnson <johnsonm@redhat.com>
- Added network-functions to spec file.
- Added report functionality to usernetctl.
- Fixed bugs I introduced into usernetctl while adding clone device support.
- Clean up entire RPM_BUILD_ROOT directory in %clean.

* Mon Sep 29 1997 Michael K. Johnson <johnsonm@redhat.com>
- Clone device support in network scripts, rc scripts, and usernetctl.
- Disassociate from controlling tty in PPP and SLIP startup scripts,
  since they act as daemons.
- Spec file now provides start/stop symlinks, since they don't fit in
  the CVS archive.

* Tue Sep 23 1997 Donnie Barnes <djb@redhat.com>
- added mktemp support to ifup

* Thu Sep 18 1997 Donnie Barnes <djb@redhat.com>
- fixed some init.d/functions bugs for stopping httpd

* Tue Sep 16 1997 Donnie Barnes <djb@redhat.com>
- reworked status() to adjust for processes that change their argv[0] in
  the process table.  The process must still have it's "name" in the argv[0]
  string (ala sendmail: blah blah).

* Mon Sep 15 1997 Erik Troan <ewt@redhat.com>
- fixed bug in FORWARD_IPV4 support

* Sun Sep 14 1997 Erik Troan <ewt@redhat.com>
- added support for FORWARD_IPV4 variable

* Thu Sep 11 1997 Donald Barnes <djb@redhat.com>
- added status function to functions along with better killproc 
  handling.
- added /sbin/usleep binary (written by me) and man page
- changed BuildRoot to /var/tmp instead of /tmp

* Tue Jun 10 1997 Michael K. Johnson <johnsonm@redhat.com>
- /sbin/netreport sgid rather than suid.
- /var/run/netreport writable by group root.

- /etc/ppp/ip-{up|down} no longer exec their local versions, so
  now ifup-post and ifdown-post will be called even if ip-up.local
  and ip-down.local exist.

* Tue Jun 03 1997 Michael K. Johnson <johnsonm@redhat.com>
- Added missing -f to [ invocation in ksyms check.

* Fri May 23 1997 Michael K. Johnson <johnsonm@redhat.com>
- Support for net event notification:
  Call /sbin/netreport to request that SIGIO be sent to you whenever
  a network interface changes status (won't work for brining up SLIP
  devices).
  Call /sbin/netreport -r to remove the notification request.
- Added ifdown-post, and made all the ifdown scrips call it, and
  added /etc/ppp/ip-down script that calls /etc/ppp/ip-down.local
  if it exists, then calls ifdown-post.
- Moved ifup and ifdown to /sbin

* Tue Apr 15 1997 Michael K. Johnson <johnsonm@redhat.com>
- usernetctl put back in ifdown
- support for slaved interfaces

* Wed Apr 02 1997 Erik Troan <ewt@redhat.com>
- Created ifup-post from old ifup
- PPP, PLIP, and generic ifup use ifup-post

* Fri Mar 28 1997 Erik Troan <ewt@redhat.com>
- Added DHCP support
- Set hostname via reverse name lookup after configuring a networking
  device if the current hostname is (none) or localhost

* Tue Mar 18 1997 Erik Troan <ewt@redhat.com>
- Got rid of xargs dependency in halt script
- Don't mount /proc twice (unmount it in between)
- sulogin and filesystem unmounting only happened for a corrupt root 
  filesystem -- it now happens when other filesystems are corrupt as well

* Tue Mar 04 1997 Michael K. Johnson <johnsonm@redhat.com>
- PPP fixes and additions

* Mon Mar 03 1997 Erik Troan <ewt@redhat.com>
- Mount proc before trying to start kerneld so we can test for /proc/ksyms
  properly.

* Wed Feb 26 1997 Michael K. Johnson <johnsonm@redhat.com>
- Added MTU for PPP.
- Put PPPOPTIONS at the end of the options string instead of at the
  beginning so that they override other options.  Gives users more rope...
- Don't do module-based stuff on non-module systems.  Ignore errors if
  st module isn't there and we try to load it.

* Tue Feb 25 1997 Michael K. Johnson <johnsonm@redhat.com>
- Changed ifup-ppp and ifdown-ppp not to use doexec, because the argv[0]
  provided by doexec goes away when pppd gets swapped out.
- ifup-ppp now sets remotename to the logical name of the device.
  This will BREAK current PAP setups on netcfg-managed interfaces,
  but we needed to do this to add a reasonable interface-specific
  PAP editor to netcfg.

* Fri Feb 07 1997 Erik Troan <ewt@redhat.com>
- Added usernetctl wrapper for user mode ifup and ifdown's and man page
- Rewrote ppp and slip kill and retry code 
- Added doexec and man page
