# Build an akmod by default. An explicit "kernels" definition makes kmodtool
# build kernel-versioned kmod packages instead.
%global buildforkernels akmod
%global debug_package %{nil}

%global kmod_name rtw88
%global commit a56bcd26e770257612a0803249cbd4095fc6feca
%global commitdate 20260521
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           %{kmod_name}-kmod
Version:        0.%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Backported Realtek rtw88 PCIe, SDIO and USB Wi-Fi kernel modules

License:        GPL-2.0-only
URL:            https://github.com/lwfinger/rtw88
Source0:        %{url}/archive/%{commit}/rtw88-%{commit}.tar.gz

Patch0:         0001-wifi-rtw88-usb-fix-beacon-download-failure-in-AP-mod.patch
Patch1:         0001-Disable-USB-2.0-USB-3.0-switch-by-default.patch

%global AkmodsBuildRequires gcc, make, patch, elfutils-libelf-devel, xz, bc, redhat-rpm-config, systemd-rpm-macros
BuildRequires:  kmodtool
BuildRequires:  %{AkmodsBuildRequires}

# kmodtool generates akmod/kmod subpackages, dependencies and scriptlets.
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description
Backported Realtek rtw88 Wi-Fi drivers for supported RTL8703, RTL8723,
RTL8811, RTL8812, RTL8814, RTL8821 and RTL8822 PCIe, SDIO and USB devices.
These modules replace the corresponding in-kernel drivers.


%package -n %{pkg_kmod_name}-common
Summary:        Common files for %{kmod_name} kernel modules
BuildArch:      noarch
Requires:       realtek-firmware


%description -n %{pkg_kmod_name}-common
Modprobe configuration to prevent the in-kernel drivers from competing
with the out-of-tree rtw88 modules.


%prep
%{?kmodtool_check}

# Print the generated template in the build log.
kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c

cd rtw88-%{commit}
%autopatch -p1
cd ..

for kernel_version in %{?kernel_versions}; do
    cp -a rtw88-%{commit} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    kver=${kernel_version%%___*}
    ksrc=${kernel_version##*___}
    make V=1 %{?_smp_mflags} \
        -C "${ksrc}" \
        M="${PWD}/_kmod_build_${kver}" \
        modules
done


%install
install -Dpm0644 rtw88-%{commit}/rtw88.conf %{buildroot}%{_modprobedir}/rtw88.conf

for kernel_version in %{?kernel_versions}; do
    kver=${kernel_version%%___*}
    moddir=%{buildroot}%{kmodinstdir_prefix}/${kver}/%{kmodinstdir_postfix}
    install -d -m 0755 "${moddir}"
    install -pm0644 _kmod_build_${kver}/rtw_*.ko "${moddir}/"
done
%{?akmod_install}


%files -n %{pkg_kmod_name}-common
%config(noreplace) %{_modprobedir}/rtw88.conf


%changelog
