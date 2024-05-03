Name:           phyre-nginx
Version:        1.25.5
Release:        1%{?dist}
Summary:       Phyre Nginx - Web server for PhyrePanel

License:       GPL
URL:    https://phyrepanel.com
Source0: https://nginx.org/download/nginx-1.25.5.tar.gz
Source1: logrotate
Source2: nginx.conf
Source3: nginx.default.conf
Source4: nginx.service
Source5: nginx.upgrade.sh
Source6: nginx.suse.logrotate
Source7: nginx-debug.service
Source8: nginx.copyright
Source9: nginx.check-reload.sh

%description


%prep
%autosetup -p1 -n nginx-1.25.5

%build
./configure --prefix=/usr/local/phyre/nginx
make
make install

%files
/usr/local/phyre/nginx

%install
rm -rf $RPM_BUILD_ROOT
%make_install

%changelog
* Tue May 03 2024 Phyre Nginx Packaging <phyre-nginx-packaging@phyrepanel.com> - 1.25.5-1%{?dist}.ngx
- 1.25.5-1
- Initial release of Phyre Nginx 1.25.5
