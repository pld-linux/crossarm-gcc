#
# MUST SEE:
#		GCC ARM Improvement Project - http://www.inf.u-szeged.hu/gcc-arm/
#
Summary:	Cross ARM GNU binary utility development utilities - gcc
Summary(es):	Utilitarios para desarrollo de binarios de la GNU - ARM gcc
Summary(fr):	Utilitaires de développement binaire de GNU - ARM gcc
Summary(pl):	Skro¶ne narzêdzia programistyczne GNU dla ARM - gcc
Summary(pt_BR):	Utilitários para desenvolvimento de binários da GNU - ARM gcc
Summary(tr):	GNU geliþtirme araçlarý - ARM gcc
Name:		crossarm-gcc
Version:	3.4.3
Release:	1.1
Epoch:		1
License:	GPL
Group:		Development/Languages
Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
# Source0-md5:	e744b30c834360fccac41eb7269a3011
%define		_llh_ver	2.6.9.1
Source1:	linux-libc-headers-%{_llh_ver}.tar.bz2
# Source1-md5:	0
Source2:	glibc-20041030.tar.bz2
# Source2-md5:	4e14871efd881fbbf523a0ba16175bc7
Patch0:		%{name}-pr15068.patch
BuildRequires:	crossarm-binutils
BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	autoconf
BuildRequires:	/bin/bash
Requires:	crossarm-binutils
Requires:	gcc-dirs
ExcludeArch:	arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		arm-pld-linux
%define		arch		%{_prefix}/%{target}
%define		gccarch		%{_libdir}/gcc/%{target}
%define		gcclib		%{gccarch}/%{version}

%define		_noautostrip	.*%{gcclib}.*/libgc.*\\.a

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

%prep
%setup -q -n gcc-%{version} -a1 -a2
%patch0 -p1

%build
FAKE_ROOT=$PWD/fake-root
%if 0
# install arm linux headers
rm -rf fake-root && mkdir -p fake-root/usr/include
cp -r linux-libc-headers-%{_llh_ver}/include/{asm-arm,linux} $FAKE_ROOT/usr/include
ln -s asm-arm $FAKE_ROOT/usr/include/asm
# build glibc headers
cd libc
rm -rf builddir && mkdir builddir && cd builddir
../configure \
	--prefix=$FAKE_ROOT/usr \
	--build=%{_target_platform} \
	--host=arm-pld-linux \
	--disable-nls \
	--with-headers=$FAKE_ROOT/usr/include \
	--disable-sanity-checks \
	--enable-hacker-mode

make sysdeps/gnu/errlist.c
make install-headers
cd -	
%endif

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
	--with-gnu-as \
	--with-gnu-ld \
	--with-system-zlib \
	--with-multilib \
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

%{target}-strip -g $RPM_BUILD_ROOT%{gcclib}/libgcov.a
%if 0%{!?debug:1}
%{target}-strip -g $RPM_BUILD_ROOT%{gcclib}/libgcc.a
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc*
%attr(755,root,root) %{_bindir}/%{target}-gcov
%dir %{gccarch}
%dir %{gcclib}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2
%{gcclib}/crt*.o
%{gcclib}/libgcc.a
%{gcclib}/specs*
%dir %{gcclib}/include
%{gcclib}/include/*.h
%{_mandir}/man1/%{target}-gcc.1*
