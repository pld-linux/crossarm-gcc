#
# MUST SEE:
#		- GCC ARM Improvement Project - http://www.inf.u-szeged.hu/gcc-arm/
#		- Developing StrongARM shellocde - http://phrack.org/show.php?p=58&a=10
#
# Conditional build:
%bcond_with	eabi		# build with Embedded ABI support
#
Summary:	Cross ARM GNU binary utility development utilities - gcc
Summary(es):	Utilitarios para desarrollo de binarios de la GNU - ARM gcc
Summary(fr):	Utilitaires de développement binaire de GNU - ARM gcc
Summary(pl):	Skro¶ne narzêdzia programistyczne GNU dla ARM - gcc
Summary(pt_BR):	Utilitários para desenvolvimento de binários da GNU - ARM gcc
Summary(tr):	GNU geliþtirme araçlarý - ARM gcc
Name:		crossarm-gcc
Version:	4.0.0
%define		_snap	20050130
Release:	0.%{_snap}.1%{?with_eabi:eabi}
Epoch:		1
License:	GPL
Group:		Development/Languages
#Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
Source0:	ftp://gcc.gnu.org/pub/gcc/snapshots/4.0-%{_snap}/gcc-4.0-%{_snap}.tar.bz2
# Source0-md5:	5040ba840d0367c378f73c739418b3e2
%define		_llh_ver	2.6.10.0
Source1:	http://ep09.pld-linux.org/~mmazur/linux-libc-headers/linux-libc-headers-%{_llh_ver}.tar.bz2
# Source1-md5:	a43c53f1bb0b586bc9bd2e8abb19e2bc
%define		_glibc_ver	2.3.4
Source2:	ftp://sources.redhat.com/pub/glibc/releases/glibc-%{_glibc_ver}.tar.bz2
# Source2-md5:	174ac5ed4f2851fcc866a3bac1e4a6a5
%define		_uclibc_ver	0.9.27
Source3:	http://uclibc.org/downloads/uClibc-%{_uclibc_ver}.tar.bz2
# Source3-md5:	6250bd6524283bd8e7bc976d43a46ec0
Source4:	crossarm-embedded-uclibc.config
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	crossarm-binutils%{?with_eabi:(eabi)}
BuildRequires:	flex
BuildRequires:	/bin/bash
Requires:	crossarm-binutils%{?with_eabi:(eabi)}
Requires:	gcc-dirs
ExcludeArch:	arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		arm-linux%{?with_eabi:-eabi}
%define		arch		%{_prefix}/%{target}
%define		gccarch		%{_libdir}/gcc/%{target}
%define		gcclib		%{gccarch}/%{version}

%define		_noautostrip	.*/libgc.*\\.a

%description
This package contains a cross-gcc which allows the creation of
binaries to be run on ARM linux (architecture arm-linux) on
other machines.

%description -l de
Dieses Paket enthält einen Cross-gcc, der es erlaubt, auf einem
anderem Rechner Code für arm-Linux zu generieren.

%description -l pl
Ten pakiet zawiera skro¶ny gcc pozwalaj±cy na robienie na innych
maszynach binariów do uruchamiania na ARM (architektura
arm-linux).

%package c++
Summary:	C++ support for crossppc-arm
Summary(pl):	Obs³uga C++ dla crossppc-arm
Group:		Development/Languages
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection for ARM.

%description c++ -l pl
Ten pakiet dodaje obs³ugê C++ do kompilatora gcc dla ARM.

%prep
%setup -q -n gcc-4.0-%{_snap} -a1 -a2 -a3

%build
FAKE_ROOT=$PWD/fake-root
rm -rf $FAKE_ROOT

%if %{with eabi}
install -d $FAKE_ROOT%{_prefix}
cp -r uClibc-%{_uclibc_ver}/* $FAKE_ROOT%{_prefix}
cd $FAKE_ROOT%{_prefix}
install %{SOURCE4} .config
%{__make} headers
%else
install -d $FAKE_ROOT%{_includedir}
cp -r linux-libc-headers-%{_llh_ver}/include/{asm-arm,linux} $FAKE_ROOT%{_includedir}
ln -s asm-arm $FAKE_ROOT%{_includedir}/asm

cd glibc-%{_glibc_ver}
cp -f /usr/share/automake/config.* scripts
rm -rf builddir && install -d builddir && cd builddir
../configure \
	--prefix=$FAKE_ROOT/usr \
	--build=%{_target_platform} \
	--host=%{target} \
	--disable-nls \
	--with-headers=$FAKE_ROOT/usr/include \
	--disable-sanity-checks \
	--enable-hacker-mode

%{__make} sysdeps/gnu/errlist.c
%{__make} install-headers

install bits/stdio_lim.h $FAKE_ROOT/usr/include/bits
touch $FAKE_ROOT/usr/include/gnu/stubs.h
%endif
cd -

cp -f /usr/share/automake/config.* .
rm -rf obj-%{target}
install -d obj-%{target}
cd obj-%{target}

CFLAGS="%{rpmcflags}" \
CXXFLAGS="%{rpmcflags}" \
TEXCONFIG=false \
../configure \
	--prefix=%{_prefix} \
	--with-sysroot=$FAKE_ROOT \
	--infodir=%{_infodir} \
	--mandir=%{_mandir} \
	--bindir=%{_bindir} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libdir} \
	--disable-shared \
	--disable-threads \
	--enable-languages="c,c++" \
	--enable-c99 \
	--enable-long-long \
	--with-gnu-as \
	--with-gnu-ld \
	--with-system-zlib \
	--with-multilib \
	--with-sysroot=$FAKE_ROOT \
	--without-x \
	--target=%{target} \
	--host=%{_target_platform} \
	--build=%{_target_platform}

%{__make} all-gcc

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C obj-%{target} install-gcc \
	DESTDIR=$RPM_BUILD_ROOT

install obj-%{target}/gcc/specs $RPM_BUILD_ROOT%{gcclib}

# don't want this here
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty.a

%if 0%{!?debug:1}
%{target}-strip -g $RPM_BUILD_ROOT%{gcclib}/libgcc.a
%{target}-strip -g $RPM_BUILD_ROOT%{gcclib}/libgcov.a
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc
%dir %{gccarch}
%dir %{gcclib}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2
%{gcclib}/crt*.o
%{gcclib}/libgcc.a
%{gcclib}/specs*
%dir %{gcclib}/include
%{gcclib}/include/*.h
%{_mandir}/man1/%{target}-cpp.1*
%{_mandir}/man1/%{target}-gcc.1*

%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclib}/cc1plus
%{_mandir}/man1/%{target}-g++.1*
