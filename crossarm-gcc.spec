#
# MUST SEE:
#		- GCC ARM Improvement Project - http://www.inf.u-szeged.hu/gcc-arm/
#		- Developing StrongARM shellocde - http://phrack.org/show.php?p=58&a=10
#
# TODO:
#		- http://gcc.gnu.org/PR18560
#
Summary:	Cross ARM GNU binary utility development utilities - gcc
Summary(es):	Utilitarios para desarrollo de binarios de la GNU - ARM gcc
Summary(fr):	Utilitaires de développement binaire de GNU - ARM gcc
Summary(pl):	Skro¶ne narzêdzia programistyczne GNU dla ARM - gcc
Summary(pt_BR):	Utilitários para desenvolvimento de binários da GNU - ARM gcc
Summary(tr):	GNU geliþtirme araçlarý - ARM gcc
Name:		crossarm-gcc
Version:	3.4.3
Release:	2
Epoch:		1
License:	GPL
Group:		Development/Languages
Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
# Source0-md5:	e744b30c834360fccac41eb7269a3011
%define		_llh_ver	2.6.10.0
Source1:	http://ep09.pld-linux.org/~mmazur/linux-libc-headers/linux-libc-headers-%{_llh_ver}.tar.bz2
# Source1-md5:	d3507b2c0203a0760a677022badcf455
Source2:	ftp://sources.redhat.com/pub/glibc/releases/glibc-2.3.4.tar.bz2
# Source2-md5:	174ac5ed4f2851fcc866a3bac1e4a6a5
Patch0:		%{name}-pr15068.patch
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	crossarm-binutils
BuildRequires:	flex
BuildRequires:	/bin/bash
Requires:	crossarm-binutils
Requires:	gcc-dirs
ExcludeArch:	arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		arm-pld-linux
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
%setup -q -n gcc-%{version} -a1 -a2
%patch0 -p1

%build
FAKE_ROOT=$PWD/fake-root

rm -rf $FAKE_ROOT && install -d $FAKE_ROOT/usr/include
cp -r linux-libc-headers-%{_llh_ver}/include/{asm-arm,linux} $FAKE_ROOT/usr/include
ln -s asm-arm $FAKE_ROOT/usr/include/asm

cd glibc-2.3.4
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
cd ../..

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
