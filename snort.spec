Name: snort
Version: 2.9.6.2
Release: 1%dist
License: GPLv2
Group: Applications/Misc
Packager: ClearFoundation
Source:  %{name}-%{version}.tar.gz
# Source: http://dl.snort.org/downloads/752
Source10: snort.conf
Source11: snort.logrotate
Source12: snort.sysv
Source14: snort-reference.config
Source100: snortsam-src-2.70.tar.gz
Source102: snortsam-state.c
Source110: snortsam.sysv
Source111: snortsam.conf
Source112: snortsam-whitelist.conf
Source113: snortsam-dns-whitelist.conf
Source200: autogen.sh
Patch1: snortsam-2.9.5.3.diff
Requires: daq >= 2.0.2
Requires: libpcap >= 1.0
Requires(pre): shadow-utils
# DNS check is done in init script
Requires: bind-utils
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: daq-devel >= 2.0.1-2
BuildRequires: daq-static >= 2.0.1-2
BuildRequires: libdnet-devel
BuildRequires: libpcap-devel >= 1.0
BuildRequires: pcre-devel
BuildRequires: perl
BuildRequires: zlib-devel
BuildRequires: flex
BuildRequires: bison
Summary: Snort intrusion detection system with SnortSam intrusion prevention

%description
Snort is a lightweight network intrusion detection system, capable of 
performing real-time traffic analysis and packet logging on IP networks.  It
can perform protocol analysis, content searching/matching and can be used to 
detect a variety of attacks and probes, such as buffer overflows, stealth port 
scans, CGI attacks, SMB probes, OS fingerprinting attempts, and much more.
SnortSam is a plugin for Snort that can perform automated blocking of IP
addresses on following firewalls: Checkpoint Firewall-1, Cisco PIX firewalls,
Cisco Routers (using ACL's), Netscreen firewalls, IP Filter (ipf, available for
various Unix-like OS'es such as FreeBSD, OpenBSD's Packet Filter (pf), Linux
IPchains, Linux IPtables, and WatchGuard Firebox firewalls.

%package devel
Summary: Snort development libraries and header files
Group: Development/Libraries
Requires: snort = %{version}-%{release}

%description devel
The snort-devel package contains libraries and header files for
developing applications that use snort.

%prep
%setup -q -n %name-%version -a 100
%patch1 -p1

%build
sh %SOURCE200
%configure \
	--bindir=%{_sbindir} \
	--sysconfdir=%{_sysconfdir}/snort.d \
	--with-libpcap-includes=%{_includedir}/pcap \
	--enable-active-response \
	--enable-decoder-preprocessor-rules \
	--enable-flexresp3 \
	--enable-gre \
	--enable-ipv6 \
	--enable-mpls \
	--enable-normalizer \
	--enable-perfprofiling \
	--enable-ppm \
	--enable-react \
	--enable-reload \
	--enable-targetbased \
	--enable-zlib \
	--without-odbc \
	--without-postgresql \
	--without-oracle \
	--without-mysql

CFLAGS="$RPM_OPT_FLAGS"
export AM_CFLAGS="-g -O2"

make

cp -v %SOURCE102 src
(cd snortsam && source ./makesnortsam.sh)
(cd snortsam && source ./makesnortsam.sh samtool)
cp -v snortsam/src/snortsam.h src/snortsam.h
(cd src && gcc -O3 -s snortsam-state.c twofish.o -o snortsam-state)

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

mkdir -p -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/rc.d/init.d
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/snortsam.d
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/snort.d/rules
mkdir -p -m 755 %{buildroot}%{_bindir}
mkdir -p -m 755 %{buildroot}%{_sbindir}
mkdir -p -m 755 %{buildroot}%{_datadir}/snort
mkdir -p -m 755 %{buildroot}%{_mandir}/man8
mkdir -p -m 755 %{buildroot}%{_libdir}/snort/dynamicengine
mkdir -p -m 755 %{buildroot}%{_libdir}/snort/dynamicpreprocessor
mkdir -p -m 755 %{buildroot}%{_localstatedir}/log/snort

install -m 0644 etc/classification.config %{buildroot}%{_sysconfdir}/snort.d/classification.config
install -m 0644 etc/unicode.map %{buildroot}%{_sysconfdir}/
install -m 0755 src/snort %{buildroot}%{_sbindir}/
install -m 0644 snort.8 %{buildroot}%{_mandir}/man8/
install -m 0644 %SOURCE10 %{buildroot}%{_datadir}/snort/snort.conf.default
install -m 0644 %SOURCE10 %{buildroot}%{_sysconfdir}/snort.conf
install -m 0644 %SOURCE11 %{buildroot}%{_sysconfdir}/logrotate.d/snort
install -m 0755 %SOURCE12 %{buildroot}%{_sysconfdir}/rc.d/init.d/snort
install -m 0644 %SOURCE14 %{buildroot}%{_sysconfdir}/snort.d/reference.config

install -m 0755 snortsam/snortsam %{buildroot}%{_sbindir}/
install -m 0755 snortsam/samtool %{buildroot}%{_sbindir}/
install -m 0755 src/snortsam-state %{buildroot}%{_bindir}/
install -m 0755 %SOURCE110 %{buildroot}%{_sysconfdir}/rc.d/init.d/snortsam
install -m 0644 %SOURCE111 %{buildroot}%{_sysconfdir}/snortsam.conf
install -m 0644 %SOURCE112 %{buildroot}%{_sysconfdir}/snortsam.d/whitelist.conf
install -m 0644 %SOURCE113 %{buildroot}%{_sysconfdir}/snortsam.d/dns-whitelist.conf

rm -rf %{buildroot}/usr/share/doc
rm -rf %{buildroot}/usr/src/snort_dynamicsrc
rm -f %{buildroot}%{_prefix}/lib/snort_dynamicrules/lib_sfdynamic_example*
rm -f %{buildroot}%{_prefix}/lib/snort_dynamicpreprocessor/lib_sfdynamic_preprocessor_example*
rm -rf %{buildroot}%{_libdir}/snort

%pre
getent group snort >/dev/null || groupadd -r snort
getent passwd snort >/dev/null || \
    useradd -r -g snort -d %{_localstatedir}/log/snort -s /sbin/nologin \
    -c "Intrusion Detection" snort
exit 0

%post
if [ $1 -eq 1 ]; then
	/sbin/chkconfig --add snort
	/sbin/chkconfig --add snortsam
fi

%preun
if [ $1 -eq 0 ]; then
	/sbin/service snort stop >/dev/null 2>&1
	/sbin/chkconfig --del snort
	/sbin/service snortsam stop >/dev/null 2>&1
	/sbin/chkconfig --del snortsam
fi

%postun
if [ $1 -ge 1 ]; then
	/sbin/service snortsam condrestart >/dev/null 2>&1
	/sbin/service snort condrestart >/dev/null 2>&1
fi

%files
%defattr(-,root,root,-)
%doc COPYING LICENSE RELEASE.NOTES doc/*
%attr(0755,snort,snort) %dir %{_localstatedir}/log/snort/
%dir %{_datadir}/snort
%{_datadir}/snort/snort.conf.default
%{_bindir}/snortsam-state
%{_sbindir}/snort
%{_sbindir}/snortsam
%{_sbindir}/samtool
%{_sbindir}/u2boat
%{_sbindir}/u2spewfoo
%{_libdir}/pkgconfig/snort.pc
%{_prefix}/lib/snort_dynamicengine
%{_prefix}/lib/snort_dynamicpreprocessor
%{_mandir}/man8/snort.8.gz
%{_sysconfdir}/unicode.map
%{_sysconfdir}/logrotate.d/snort
%{_sysconfdir}/rc.d/init.d/snort
%{_sysconfdir}/rc.d/init.d/snortsam
%{_sysconfdir}/snort.d/classification.config
%{_sysconfdir}/snort.d/reference.config
%dir %{_sysconfdir}/snort.d
%dir %{_sysconfdir}/snort.d/rules
%dir %{_sysconfdir}/snortsam.d
%config(noreplace) %{_sysconfdir}/snort.conf
%config(noreplace) %{_sysconfdir}/snort.conf
%config(noreplace) %{_sysconfdir}/snortsam.conf
%config(noreplace) %{_sysconfdir}/snortsam.d/whitelist.conf
%config(noreplace) %{_sysconfdir}/snortsam.d/dns-whitelist.conf

%files devel
%dir /usr/include/snort/
/usr/include/snort/
%{_libdir}/pkgconfig/snort_output.pc
%{_libdir}/pkgconfig/snort_preproc.pc

%changelog
* Wed Feb 19 2014 ClearFoundation <developer@clearfoundation.com> - 2.9.5.3-2.clear
- Added requirement for daq >= 2.0.1-2

* Thu Oct 17 2013 ClearFoundation <developer@clearfoundation.com> - 2.9.5.3-3.clear
- Added workaround for PPPoE interfaces [tracker #1380]

* Wed Sep 18 2013 ClearFoundation <developer@clearfoundation.com> - 2.9.5.3-2.clear
- Added requirement for daq >= 2.0.0

* Tue Sep 17 2013 ClearFoundation <developer@clearfoundation.com> - 2.9.5.3-1.clear
- Updated to 2.9.5.3

* Wed Aug 14 2013 ClearFoundation <developer@clearfoundation.com> - 2.9.0.4-4.clear
- Cleaned up logrotate [tracker #1130]
- Removed old network auto-configuration [tracker #1225]

* Thu Nov 24 2011 ClearFoundation <developer@clearfoundation.com> - 2.9.0.4-3.clear
- Added a workaround for broken PID handling

* Thu Nov 17 2011 ClearFoundation <developer@clearfoundation.com> - 2.9.0.4-2.clear
- Changed chkconfig defaults

