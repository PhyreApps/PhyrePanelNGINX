#
%define nginx_home %{_localstatedir}/cache/phyre-nginx
%define nginx_user nginx
%define nginx_group nginx
%define nginx_loggroup adm

BuildRequires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%if 0%{?rhel}
%define _group System Environment/Daemons
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 0)
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: openssl >= 1.0.2
Requires: procps-ng
BuildRequires: openssl-devel >= 1.0.2
%define dist .el7
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 2)
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: openssl11 >= 1.1.1
Requires: procps-ng
BuildRequires: openssl11-devel >= 1.1.1
%endif

%if 0%{?rhel} == 8
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: procps-ng
BuildRequires: openssl-devel >= 1.1.1
%define _debugsource_template %{nil}
%endif

%if 0%{?rhel} == 9
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: procps-ng
BuildRequires: openssl-devel
%define _debugsource_template %{nil}
%endif

%if 0%{?suse_version} >= 1315
%define _group Productivity/Networking/Web/Servers
%define nginx_loggroup trusted
Requires(pre): shadow
Requires: procps
BuildRequires: libopenssl-devel
%define _debugsource_template %{nil}
%endif

# This also applies to Amazon Linux 2023
%if 0%{?fedora}
%define _debugsource_template %{nil}
%global _hardened_build 1
%define _group System Environment/Daemons
Requires: procps-ng
BuildRequires: openssl-devel
Requires(pre): shadow-utils
%endif

# end of distribution specific definitions

%define base_version 1.25.5
%define base_release 1%{?dist}.ngx

%define bdir %{_builddir}/%{name}-%{base_version}

%define WITH_CC_OPT $(echo %{optflags} $(pcre2-config --cflags)) -fPIC
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now -pie

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/phyre-nginx --sbin-path=%{_sbindir}/phyre-nginx --modules-path=%{_libdir}/phyre-nginx/modules --conf-path=%{_sysconfdir}/phyre-nginx/phyre-nginx.conf --error-log-path=%{_localstatedir}/log/phyre-nginx/error.log --http-log-path=%{_localstatedir}/log/phyre-nginx/access.log --pid-path=%{_localstatedir}/run/phyre-nginx.pid --lock-path=%{_localstatedir}/run/phyre-nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/phyre-nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/phyre-nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/phyre-nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/phyre-nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/phyre-nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module $( if [ 0%{?rhel} -eq 7 ] || [ 0%{?suse_version} -eq 1315 ]; then continue; else echo "--with-http_v3_module"; fi; ) --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")

Summary: High performance web server
Name: phyre-nginx
Version: %{base_version}
Release: %{base_release}
Vendor: NGINX Packaging <nginx-packaging@f5.com>
URL: https://phyre-nginx.org/
Group: %{_group}

Source0: https://phyre-nginx.org/download/%{name}-%{version}.tar.gz
Source1: logrotate
Source2: phyre-nginx.conf
Source3: phyre-nginx.default.conf
Source4: phyre-nginx.service
Source5: phyre-nginx.upgrade.sh
Source6: phyre-nginx.suse.logrotate
Source7: phyre-nginx-debug.service
Source8: phyre-nginx.copyright
Source9: phyre-nginx.check-reload.sh



License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{base_version}-%{base_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre2-devel

Provides: webserver
Provides: nginx-r%{base_version}

%if !(0%{?rhel} == 7)
Recommends: logrotate
%endif

%description
nginx [engine x] is an HTTP and reverse proxy server, as well as
a mail proxy server.

%if 0%{?suse_version} >= 1315
%debug_package
%endif

%prep
%autosetup -p1

%build
./configure %{BASE_CONFIGURE_ARGS} \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}" \
    --with-debug
make %{?_smp_mflags}
%{__mv} %{bdir}/objs/nginx \
    %{bdir}/objs/nginx-debug
./configure %{BASE_CONFIGURE_ARGS} \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}"
make %{?_smp_mflags}

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT INSTALLDIRS=vendor install

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/phyre-nginx
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/html $RPM_BUILD_ROOT%{_datadir}/phyre-nginx/

%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/*.default
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/fastcgi.conf

%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/phyre-nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/run/phyre-nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/cache/phyre-nginx

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/phyre-nginx/modules
cd $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx && \
    %{__ln_s} ../..%{_libdir}/phyre-nginx/modules modules && cd -

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{base_version}
%{__install} -m 644 -p %{SOURCE8} \
    $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{base_version}/COPYRIGHT

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/conf.d
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/phyre-nginx.conf
%{__install} -m 644 -p %{SOURCE2} \
    $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/phyre-nginx.conf
%{__install} -m 644 -p %{SOURCE3} \
    $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/conf.d/default.conf

%{__install} -p -D -m 0644 %{bdir}/objs/nginx.8 \
    $RPM_BUILD_ROOT%{_mandir}/man8/nginx.8

%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
%{__install} -m644 %SOURCE4 \
    $RPM_BUILD_ROOT%{_unitdir}/phyre-nginx.service
%{__install} -m644 %SOURCE7 \
    $RPM_BUILD_ROOT%{_unitdir}/phyre-nginx-debug.service
%{__mkdir} -p $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/phyre-nginx
%{__install} -m755 %SOURCE5 \
    $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/phyre-nginx/upgrade
%{__install} -m755 %SOURCE9 \
    $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/phyre-nginx/check-reload

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%if 0%{?suse_version}
%{__install} -m 644 -p %{SOURCE6} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/phyre-nginx
%else
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/phyre-nginx
%endif

%{__install} -m755 %{bdir}/objs/nginx-debug \
    $RPM_BUILD_ROOT%{_sbindir}/nginx-debug

%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/koi-utf
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/koi-win
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/phyre-nginx/win-utf

%check
%{__rm} -rf $RPM_BUILD_ROOT/usr/src
cd %{bdir}
grep -v 'usr/src' debugfiles.list > debugfiles.list.new && mv debugfiles.list.new debugfiles.list
cat /dev/null > debugsources.list
%if 0%{?suse_version} >= 1500
cat /dev/null > debugsourcefiles.list
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%{_sbindir}/phyre-nginx
%{_sbindir}/phyre-nginx-debug

%dir %{_sysconfdir}/phyre-nginx
%dir %{_sysconfdir}/phyre-nginx/conf.d
%{_sysconfdir}/phyre-nginx/modules

%config(noreplace) %{_sysconfdir}/phyre-nginx/phyre-nginx.conf
%config(noreplace) %{_sysconfdir}/phyre-nginx/conf.d/default.conf
%config(noreplace) %{_sysconfdir}/phyre-nginx/mime.types
%config(noreplace) %{_sysconfdir}/phyre-nginx/fastcgi_params
%config(noreplace) %{_sysconfdir}/phyre-nginx/scgi_params
%config(noreplace) %{_sysconfdir}/phyre-nginx/uwsgi_params

%config(noreplace) %{_sysconfdir}/logrotate.d/phyre-nginx
%{_unitdir}/phyre-nginx.service
%{_unitdir}/phyre-nginx-debug.service
%dir %{_libexecdir}/initscripts/legacy-actions/phyre-nginx
%{_libexecdir}/initscripts/legacy-actions/phyre-nginx/*

%attr(0755,root,root) %dir %{_libdir}/phyre-nginx
%attr(0755,root,root) %dir %{_libdir}/phyre-nginx/modules
%dir %{_datadir}/phyre-nginx
%dir %{_datadir}/phyre-nginx/html
%{_datadir}/phyre-nginx/html/*

%attr(0755,root,root) %dir %{_localstatedir}/cache/phyre-nginx
%attr(0755,root,root) %dir %{_localstatedir}/log/phyre-nginx

%dir %{_datadir}/doc/%{name}-%{base_version}
%doc %{_datadir}/doc/%{name}-%{base_version}/COPYRIGHT
%{_mandir}/man8/phyre-nginx.8*

%pre
# Add the "nginx" user
getent group %{nginx_group} >/dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} >/dev/null || \
    useradd -r -g %{nginx_group} -s /sbin/nologin \
    -d %{nginx_home} -c "nginx user"  %{nginx_user}
exit 0

%post
# Register the nginx service
if [ $1 -eq 1 ]; then
    /usr/bin/systemctl preset phyre-nginx.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl preset phyre-nginx-debug.service >/dev/null 2>&1 ||:
    # print site info
    cat <<BANNER
----------------------------------------------------------------------

Thanks for using nginx!

Please find the official documentation for nginx here:
* https://phyre-nginx.org/en/docs/

Please subscribe to nginx-announce mailing list to get
the most important news about nginx:
* https://phyre-nginx.org/en/support.html

Commercial subscriptions for nginx are available on:
* https://phyre-nginx.com/products/

----------------------------------------------------------------------
BANNER

    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/phyre-nginx ]; then
        if [ ! -e %{_localstatedir}/log/phyre-nginx/access.log ]; then
            touch %{_localstatedir}/log/phyre-nginx/access.log
            %{__chmod} 640 %{_localstatedir}/log/phyre-nginx/access.log
            %{__chown} nginx:%{nginx_loggroup} %{_localstatedir}/log/phyre-nginx/access.log
        fi

        if [ ! -e %{_localstatedir}/log/phyre-nginx/error.log ]; then
            touch %{_localstatedir}/log/phyre-nginx/error.log
            %{__chmod} 640 %{_localstatedir}/log/phyre-nginx/error.log
            %{__chown} phyre-nginx:%{nginx_loggroup} %{_localstatedir}/log/phyre-nginx/error.log
        fi
    fi
fi

%preun
if [ $1 -eq 0 ]; then
    /usr/bin/systemctl --no-reload disable phyre-nginx.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl stop phyre-nginx.service >/dev/null 2>&1 ||:
fi

%postun
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
if [ $1 -ge 1 ]; then
    /sbin/service phyre-nginx status  >/dev/null 2>&1 || exit 0
    /sbin/service phyre-nginx upgrade >/dev/null 2>&1 || echo \
        "Binary upgrade failed, please check nginx's error.log"
fi


%changelog
* Tue May 03 2024 Phyre Nginx Packaging <phyre-nginx-packaging@phyrepanel.com> - 1.25.5-1%{?dist}.ngx
- 1.25.5-1
- Initial release of Phyre Nginx 1.25.5
