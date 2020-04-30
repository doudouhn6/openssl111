%define soversion 1.1
%define optprefix /opt/codeit/openssl111
%define enginesdir %{optprefix}engines

# Number of threads to spawn when testing some threading fixes.
%define thread_test_threads %{?threads:%{threads}}%{!?threads:1}

# Arches on which we need to prevent arch conflicts on opensslconf.h, must
# also be handled in opensslconf-new.h.
%define multilib_arches %{ix86} ia64 %{mips} ppc %{power64} s390 s390x sparcv9 sparc64 x86_64

%global _performance_build 1

Summary: Utilities from the general purpose cryptography library with TLS implementation
Name: openssl111
Version: 1.1.1g
Release: 2.codeit%{?dist}
Source: https://www.openssl.org/source/openssl-%{version}.tar.gz
Source1: openssl-1.1.1-x86_64.conf

# Build changes
Patch1: openssl-1.1.1-build.patch
Patch2: openssl-1.1.1-defaults.patch
Patch3: openssl-1.1.1-no-html.patch
Patch4: openssl-1.1.1-man-rename.patch
# Bug fixes
Patch21: openssl-1.1.0-issuer-hash.patch
# Functionality changes
Patch31: openssl-1.1.1-conf-paths.patch
Patch32: openssl-1.1.1-version-add-engines.patch
Patch33: openssl-1.1.1-apps-dgst.patch
Patch36: openssl-1.1.1-no-brainpool.patch
Patch37: openssl-1.1.1-ec-curves.patch
Patch38: openssl-1.1.1-no-weak-verify.patch
Patch40: openssl-1.1.1-disable-ssl3.patch
Patch41: openssl-1.1.1-system-cipherlist.patch
Patch42: openssl-1.1.1-fips.patch
Patch43: openssl-1.1.1-ignore-bound.patch
Patch44: openssl-1.1.1-version-override.patch
Patch45: openssl-1.1.1-weak-ciphers.patch
Patch46: openssl-1.1.1-seclevel.patch
Patch47: openssl-1.1.1-ts-sha256-default.patch
Patch48: openssl-1.1.1-fips-post-rand.patch
Patch49: openssl-1.1.1-evp-kdf.patch
Patch50: openssl-1.1.1-ssh-kdf.patch
Patch60: openssl-1.1.1-krb5-kdf.patch
Patch61: openssl-1.1.1-intel-cet.patch
Patch65: openssl-1.1.1-fips-drbg-selftest.patch
# Backported fixes including security fixes
Patch52: openssl-1.1.1-s390x-update.patch
Patch53: openssl-1.1.1-fips-crng-test.patch

License: OpenSSL
Group: System Environment/Libraries
URL: http://www.openssl.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: coreutils, krb5-devel, perl, sed, zlib-devel, /usr/bin/cmp
BuildRequires: lksctp-tools-devel
BuildRequires: /usr/bin/rename
BuildRequires: /usr/bin/pod2man
Requires: coreutils, make
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description
The OpenSSL toolkit provides support for secure communications between
machines. OpenSSL includes a certificate management tool and shared
libraries which provide various cryptographic algorithms and
protocols.

%package libs
Summary: A general purpose cryptography library with TLS implementation
Group: System Environment/Libraries
Requires: ca-certificates >= 2008-5

%description libs
OpenSSL is a toolkit for supporting cryptography. The openssl-libs
package contains the libraries that are used by various applications which
support cryptographic algorithms and protocols.

%package devel
Summary: Files for development of applications which will use OpenSSL
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: krb5-devel%{?_isa}, zlib-devel%{?_isa}
Requires: pkgconfig

%description devel
OpenSSL is a toolkit for supporting cryptography. The openssl-devel
package contains include files needed to develop applications which
support various cryptographic algorithms and protocols.

%global debug_package %{nil}

%prep
%setup -q -n openssl-%{version}

%patch1 -p1 -b .build   %{?_rawbuild}
%patch2 -p1 -b .defaults
%patch3 -p1 -b .no-html  %{?_rawbuild}
%patch4 -p1 -b .man-rename

%patch21 -p1 -b .issuer-hash

%patch31 -p1 -b .conf-paths
%patch32 -p1 -b .version-add-engines
%patch33 -p1 -b .dgst
%patch36 -p1 -b .no-brainpool
%patch37 -p1 -b .curves
%patch38 -p1 -b .no-weak-verify
%patch40 -p1 -b .disable-ssl3
%patch41 -p1 -b .system-cipherlist
%patch42 -p1 -b .fips
%patch43 -p1 -b .ignore-bound
%patch44 -p1 -b .version-override
%patch45 -p1 -b .weak-ciphers
%patch46 -p1 -b .seclevel
%patch47 -p1 -b .ts-sha256-default
%patch48 -p1 -b .fips-post-rand
%patch49 -p1 -b .evp-kdf
%patch50 -p1 -b .ssh-kdf
%patch52 -p1 -b .s390x-update
%patch53 -p1 -b .crng-test
%patch60 -p1 -b .krb5-kdf
%patch61 -p1 -b .intel-cet
%patch65 -p1 -b .drbg-selftest

%build
# ia64, x86_64, ppc are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.
./Configure \
	--prefix=%{optprefix} --openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
	no-ssl2 no-ssl3 no-comp no-idea no-dtls no-dtls1 no-weak-ssl-ciphers \
	no-md4 no-dtls1-method no-dtls1_2-method \
	linux-x86_64

# Add -Wa,--noexecstack here so that libcrypto's assembler modules will be
# marked as not requiring an executable stack.
# Also add -DPURIFY to make using valgrind with openssl easier as we do not
# want to depend on the uninitialized memory as a source of entropy anyway.
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -Wa,--noexecstack -DPURIFY"
make depend
make all

# Clean up the .pc files
for i in libcrypto.pc libssl.pc openssl.pc ; do
  sed -i '/^Libs.private:/{s/-L[^ ]* //;s/-Wl[^ ]* //}' $i
done

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
# Install OpenSSL.
install -d $RPM_BUILD_ROOT/opt
make DESTDIR=$RPM_BUILD_ROOT install_sw

rm -rf $RPM_BUILD_ROOT/%{optprefix}/lib/libcrypto.a
rm -rf $RPM_BUILD_ROOT/%{optprefix}/lib/libssl.a

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d
cp %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/openssl-1.1.1-x86_64.conf

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%license LICENSE
%doc FAQ NEWS README README.FIPS
%{optprefix}/bin/*

%files libs
%defattr(-,root,root)
%license LICENSE
%{_sysconfdir}/ld.so.conf.d/openssl-1.1.1-x86_64.conf
%attr(0755,root,root) %{optprefix}/lib/libcrypto.so.%{soversion}
%attr(0755,root,root) %{optprefix}/lib/libcrypto.so
%attr(0755,root,root) %{optprefix}/lib/libssl.so.%{soversion}
%attr(0755,root,root) %{optprefix}/lib/libssl.so
%attr(0755,root,root) %{optprefix}/lib/engines-%{soversion}

%files devel
%defattr(-,root,root)
%{optprefix}/include
%attr(0644,root,root) %{optprefix}/lib/pkgconfig/*.pc

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

