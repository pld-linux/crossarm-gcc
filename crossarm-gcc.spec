#
# MUST SEE:
#		- GCC ARM Improvement Project - http://www.inf.u-szeged.hu/gcc-arm/
#		- Developing StrongARM shellocde - http://phrack.org/show.php?p=58&a=10
#
# Conditional build:
%bcond_without	gnueabi		# build without Embedded ABI support
#
Summary:	Cross ARM GNU binary utility development utilities - gcc
Summary(es.UTF-8):	Utilitarios para desarrollo de binarios de la GNU - ARM gcc
Summary(fr.UTF-8):	Utilitaires de développement binaire de GNU - ARM gcc
Summary(pl.UTF-8):	Skrośne narzędzia programistyczne GNU dla ARM - gcc
Summary(pt_BR.UTF-8):	Utilitários para desenvolvimento de binários da GNU - ARM gcc
Summary(tr.UTF-8):	GNU geliştirme araçları - ARM gcc
Name:		crossarm-gcc
Version:	4.2.2
Release:	1%{?with_gnueabi:gnueabi}
Epoch:		1
License:	GPL
Group:		Development/Languages
Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
# Source0-md5:	7ae33781417a35a2eb03ee098a9f4490
%define		_llh_ver	2.6.12.0
Source1:	http://ep09.pld-linux.org/~mmazur/linux-libc-headers/linux-libc-headers-%{_llh_ver}.tar.bz2
# Source1-md5:	eae2f562afe224ad50f65a6acfb4252c
%define		_uclibc_ver	0.9.27
Source2:	http://uclibc.org/downloads/uClibc-%{_uclibc_ver}.tar.bz2
# Source2-md5:	6250bd6524283bd8e7bc976d43a46ec0
Source3:	crossarm-embedded-uclibc.config
Source4:	crossarm-lpc210x-crt0.s
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	crossarm-binutils%{?with_gnueabi:(gnueabi)}
BuildRequires:	flex
BuildRequires:	kernel-module-build
Requires:	crossarm-binutils%{?with_gnueabi:(gnueabi)}
Requires:	gcc-dirs
ExcludeArch:	arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		arm-linux%{?with_gnueabi:-gnueabi}
%define		arch		%{_prefix}/%{target}
%define		gccarch		%{_libdir}/gcc/%{target}
%define		gcclib		%{gccarch}/%{version}

%define		_noautostrip	.*/libgc.*\\.a

%description
This package contains a cross-gcc which allows the creation of
binaries to be run on ARM Linux on other machines.

%description -l de.UTF-8
Dieses Paket enthält einen Cross-gcc, der es erlaubt, auf einem
anderem Rechner Code für ARM Linux zu generieren.

%description -l pl.UTF-8
Ten pakiet zawiera skrośny gcc pozwalający na robienie na innych
maszynach binariów do uruchamiania na Linuksie ARM.

%package c++
Summary:	C++ support for crossarm-gcc
Summary(pl.UTF-8):	Obsługa C++ dla crossarm-gcc
Group:		Development/Languages
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection for ARM.

%description c++ -l pl.UTF-8
Ten pakiet dodaje obsługę C++ do kompilatora gcc dla ARM.

%prep
%setup -q -n gcc-%{version} -a1 -a2

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

XCFLAGS="%{rpmcflags}" \
XCXXFLAGS="%{rpmcxxflags}" \
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
install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

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
install %{SOURCE4} $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
%{target}-as -mcpu=arm7tdmi %{SOURCE4} -o $RPM_BUILD_ROOT%{gcclib}/lpc210x-crt0.o

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc
%attr(755,root,root) %{_bindir}/%{target}-gcc-%{version}
%attr(755,root,root) %{_bindir}/%{target}-gcov
%dir %{gccarch}
%dir %{gcclib}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2
%{gcclib}/*crt*.o
%{gcclib}/libgcc.a
%{gcclib}/libgcov.a
%{gcclib}/specs*
%dir %{gcclib}/include
%{gcclib}/include/*.h
%{_mandir}/man1/%{target}-cpp.1*
%{_mandir}/man1/%{target}-gcc.1*
%{_mandir}/man1/%{target}-gcov.1*
%{_examplesdir}/%{name}-%{version}

%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-c++
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclib}/cc1plus
%{_mandir}/man1/%{target}-g++.1*
