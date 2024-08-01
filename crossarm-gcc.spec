#
# MUST SEE:
#		- GCC ARM Improvement Project - http://www.inf.u-szeged.hu/gcc-arm/
#		- Developing StrongARM shellocde - http://phrack.org/show.php?p=58&a=10

Summary:	Cross ARM GNU binary utility development utilities - gcc
Summary(es.UTF-8):	Utilitarios para desarrollo de binarios de la GNU - ARM gcc
Summary(fr.UTF-8):	Utilitaires de développement binaire de GNU - ARM gcc
Summary(pl.UTF-8):	Skrośne narzędzia programistyczne GNU dla ARM - gcc
Summary(pt_BR.UTF-8):	Utilitários para desenvolvimento de binários da GNU - ARM gcc
Summary(tr.UTF-8):	GNU geliştirme araçları - ARM gcc
Name:		crossarm-gcc
Version:	14.2.0
Release:	1
Epoch:		1
License:	GPL
Group:		Development/Languages
Source0:	https://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.xz
# Source0-md5:	2268420ba02dc01821960e274711bde0
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf >= 2.64
BuildRequires:	automake >= 1:1.11.1
BuildRequires:	bison
BuildRequires:	crossarm-binutils >= 2.30
BuildRequires:	flex >= 2.5.4
BuildRequires:	gmp-devel >= 4.3.2
BuildRequires:	isl-devel >= 0.15
BuildRequires:	libmpc-devel >= 0.8.1
BuildRequires:	libstdc++-devel
BuildRequires:	mpfr-devel >= 3.1.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel
Requires:	crossarm-binutils >= 2.30
Requires:	gcc-dirs
Requires:	gmp >= 4.3.2
Requires:	isl >= 0.15
Requires:	libmpc >= 0.8.1
Requires:	mpfr >= 3.1.0
ExcludeArch:	%{arm}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		arm-linux-gnueabi
%define		arch		%{_prefix}/%{target}
%define		gccarch		%{_libdir}/gcc/%{target}
%define		gcclib		%{gccarch}/%{version}
%define		filterout	-Werror=format-security

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
%setup -q -n gcc-%{version}

%build
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
	--without-x \
	--target=%{target} \
	--host=%{_target_platform} \
	--build=%{_target_platform}

%{__make} all-gcc
%{__make} all-target-libgcc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%{__make} -C obj-%{target} install-gcc install-target-libgcc \
	DESTDIR=$RPM_BUILD_ROOT

install obj-%{target}/gcc/specs $RPM_BUILD_ROOT%{gcclib}

# don't want this here
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty.a

# include/ contains install-tools/include/* and headers that were fixed up
# by fixincludes, we don't want former
gccdir=$(echo $RPM_BUILD_ROOT%{_libdir}/gcc/*/*/)
cp -f	$gccdir/install-tools/include/*.h $gccdir/include
# but we don't want anything more from install-tools
rm -rf	$gccdir/install-tools

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc
%attr(755,root,root) %{_bindir}/%{target}-gcc-%{version}
%attr(755,root,root) %{_bindir}/%{target}-gcc-ar
%attr(755,root,root) %{_bindir}/%{target}-gcc-nm
%attr(755,root,root) %{_bindir}/%{target}-gcc-ranlib
%attr(755,root,root) %{_bindir}/%{target}-gcov
%attr(755,root,root) %{_bindir}/%{target}-gcov-dump
%attr(755,root,root) %{_bindir}/%{target}-gcov-tool
%attr(755,root,root) %{_bindir}/%{target}-lto-dump
%dir %{gccarch}
%dir %{gcclib}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2
%attr(755,root,root) %{gcclib}/lto-wrapper
%attr(755,root,root) %{gcclib}/lto1
%attr(755,root,root) %{gcclib}/liblto_plugin.so*
%{gcclib}/*crt*.o
%{gcclib}/libgcc.a
%{gcclib}/libgcov.a
%{gcclib}/specs*
%dir %{gcclib}/include
%{gcclib}/include/*.h
%{_mandir}/man1/%{target}-cpp.1*
%{_mandir}/man1/%{target}-gcc.1*
%{_mandir}/man1/%{target}-gcov.1*
%{_mandir}/man1/%{target}-gcov-dump.1*
%{_mandir}/man1/%{target}-gcov-tool.1*
%{_mandir}/man1/%{target}-lto-dump.1*
%{_examplesdir}/%{name}-%{version}

%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-c++
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclib}/cc1plus
%{_mandir}/man1/%{target}-g++.1*
