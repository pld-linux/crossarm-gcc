#
# MUST SEE:
#		- GCC ARM Improvement Project - http://www.inf.u-szeged.hu/gcc-arm/
#		- Developing StrongARM shellocde - http://phrack.org/show.php?p=58&a=10
#
# Conditional build:
%bcond_without	eabi		# build without Embedded ABI support
#
Summary:	Cross ARM GNU binary utility development utilities - gcc
Summary(es):	Utilitarios para desarrollo de binarios de la GNU - ARM gcc
Summary(fr):	Utilitaires de développement binaire de GNU - ARM gcc
Summary(pl):	Skro¶ne narzêdzia programistyczne GNU dla ARM - gcc
Summary(pt_BR):	Utilitários para desenvolvimento de binários da GNU - ARM gcc
Summary(tr):	GNU geliþtirme araçlarý - ARM gcc
Name:		crossarm-gcc
Version:	4.0.1
#define		_snap	20050609
Release:	1
Epoch:		1
License:	GPL
Group:		Development/Languages
Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
# Source0-md5:	947416e825a877a0d69489be1be43be1
#Source0:	ftp://gcc.gnu.org/pub/gcc/snapshots/4.0-%{_snap}/gcc-4.0-%{_snap}.tar.bz2
%define		_llh_ver	2.6.11.2
Source1:	http://ep09.pld-linux.org/~mmazur/linux-libc-headers/linux-libc-headers-%{_llh_ver}.tar.bz2
# Source1-md5:	2d21d8e7ff641da74272b114c786464e
%define		_uclibc_ver	0.9.27
Source2:	http://uclibc.org/downloads/uClibc-%{_uclibc_ver}.tar.bz2
# Source2-md5:	6250bd6524283bd8e7bc976d43a46ec0
Source3:	crossarm-embedded-uclibc.config
Source4:	crossarm-lpc210x-crt0.s
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	crossarm-binutils%{?with_eabi:(eabi)}
BuildRequires:	flex
BuildRequires:	kernel-module-build
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
binaries to be run on ARM Linux on other machines.

%description -l de
Dieses Paket enthält einen Cross-gcc, der es erlaubt, auf einem
anderem Rechner Code für ARM Linux zu generieren.

%description -l pl
Ten pakiet zawiera skro¶ny gcc pozwalaj±cy na robienie na innych
maszynach binariów do uruchamiania na Linuksie ARM.

%package c++
Summary:	C++ support for crossarm-gcc
Summary(pl):	Obs³uga C++ dla crossarm-gcc
Group:		Development/Languages
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection for ARM.

%description c++ -l pl
Ten pakiet dodaje obs³ugê C++ do kompilatora gcc dla ARM.

%prep
%setup -q -n gcc-%{version} -a1 -a2
#setup -q -n gcc-4.0-%{_snap} -a1 -a2

%build
FAKE_ROOT=$PWD/fake-root
rm -rf $FAKE_ROOT

install -d $FAKE_ROOT%{_prefix}
cp -r uClibc-%{_uclibc_ver}/* $FAKE_ROOT%{_prefix}
cd $FAKE_ROOT%{_prefix}
install %{SOURCE3} .config
%{__make} headers
cd -

cp -f /usr/share/automake/config.* .
rm -rf obj-%{target}
install -d obj-%{target}
cd obj-%{target}

CFLAGS="%{rpmcflags}" \
CXXFLAGS="%{rpmcxxflags}" \
TEXCONFIG=false \
../configure \
	--prefix=%{_prefix} \
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
	--disable-nls \
	--with-gnu-as \
	--with-gnu-ld \
	--with-demangler-in-ld \
	--with-system-zlib \
	--enable-multilib \
	--with-sysroot=$FAKE_ROOT \
	--without-x \
	--target=%{target} \
	--host=%{_target_platform} \
	--build=%{_target_platform}

%{__make} all-gcc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{name}

%{__make} -C obj-%{target} install-gcc \
	DESTDIR=$RPM_BUILD_ROOT

install obj-%{target}/gcc/specs $RPM_BUILD_ROOT%{gcclib}

# don't want this here
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty.a

# include/ contains install-tools/include/* and headers that were fixed up
# by fixincludes, we don't want former
gccdir=$(echo $RPM_BUILD_ROOT%{_libdir}/gcc/*/*/)
mkdir	$gccdir/tmp
# we have to save these however
#{?with_java:mv -f $gccdir/include/{gcj,libffi/ffitarget.h} $gccdir/tmp}
mv -f	$gccdir/include/syslimits.h $gccdir/tmp
rm -rf	$gccdir/include
mv -f	$gccdir/tmp $gccdir/include
cp -f	$gccdir/install-tools/include/*.h $gccdir/include
# but we don't want anything more from install-tools
rm -rf	$gccdir/install-tools

%if 0%{!?debug:1}
%{target}-strip -g -R.note -R.comment $RPM_BUILD_ROOT%{gcclib}/libgcc.a
%{target}-strip -g -R.note -R.comment $RPM_BUILD_ROOT%{gcclib}/libgcov.a
%endif

# custom startup file(s)
install %{SOURCE4} $RPM_BUILD_ROOT%{_usrsrc}/%{name}
%{target}-as -mcpu=arm7tdmi %{SOURCE4} -o $RPM_BUILD_ROOT%{gcclib}/lpc210x-crt0.o

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc
%dir %{gccarch}
%dir %{gcclib}
%{?with_eabi:%dir %{gcclib}/thumb}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2
%{gcclib}/*crt*.o
%{gcclib}/libgcc.a
%if %{with eabi}
%{gcclib}/thumb/crt*.o
%{gcclib}/thumb/libgcc.a
%endif
%{gcclib}/specs*
%dir %{gcclib}/include
%{gcclib}/include/*.h
%{_mandir}/man1/%{target}-cpp.1*
%{_mandir}/man1/%{target}-gcc.1*
%{_usrsrc}/%{name}

%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclib}/cc1plus
%{_mandir}/man1/%{target}-g++.1*
