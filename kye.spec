Summary:	Clone of the classic Kye puzzle game
Name:		kye
Version:	1.0
Release:	1
Packager:	Colin Phipps <cph@moria.org.uk>
Vendor:		http://games.moria.org.uk/
Source:		http://games.moria.org.uk/kye/download/%{name}-%{version}.tar.gz
License:	GPLv2+
Group:		Amusements/Games
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix:		%{_prefix}
Url:		http://games.moria.org.uk/kye/pygtk
BuildArch:	noarch
BuildRequires: python-devel
BuildRequires: desktop-file-utils
BuildRequires: pygtk2

%description
This is a clone of the game Kye for Windows, originally by Colin Garbutt. It
is a puzzle game, which is a little like the old falling-rocks puzzle games,
and perhaps also inspired a little by Sokoban. But Kye has more variety of
objects, and so is capable of posing quite complex puzzles.


%prep
%setup -q

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
cp kye*icon.png  $RPM_BUILD_ROOT%{_datadir}/pixmaps/

cat << EOF >> %{name}.desktop
[Desktop Entry]
Type=Application
Version=1.0
Name=Kye
Icon=kye-icon.png
Exec=Kye %f
Terminal=false
Categories=Game;LogicGame;
EOF

cat << EOF >> %{name}-edit.desktop
[Desktop Entry]
Type=Application
Version=1.0
Name=Kye Level Editor
Exec=Kye-edit %f
Icon=kye-edit-icon.png
Terminal=false
Categories=Game;LogicGame;
EOF


mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
desktop-file-install --dir $RPM_BUILD_ROOT/%{_datadir}/applications/ \
		     --vendor moria-org \
		     %{name}.desktop

desktop-file-install --dir $RPM_BUILD_ROOT/%{_datadir}/applications/ \
		     --vendor moria-org \
		     %{name}-edit.desktop
							       

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc NEWS README COPYING
%{_datadir}/pixmaps/*.png
%{_datadir}/applications/*.desktop

%changelog
* Wed Dec 15 2010 Colin Phipps <cph@moria.org.uk> - 1.0-1
- no significant changes.

* Wed Sep 15 2010 Colin Phipps <cph@moria.org.uk> - 0.9.6-1
- code tweaks, no effect for the Linux version.

* Tue Sep 07 2010 Colin Phipps <cph@moria.org.uk> - 0.9.5-1
- improve various error-handling code paths.
- minor RPM spec file improvements.

* Sat Apr 03 2010 Colin Phipps <cph@moria.org.uk> - 0.9.4-1
- workaround change in librsvg - CSS selector specificity seems to no longer take ID selectors into account? This affected rendering of many of the tiles.
- improve level complete dialog box.
- improve error feedback when tileset is not found.
- update for GTK 2.12.
- lots of changelog omitted here...

* Fri Mar 24 2006 Colin Phipps <cph@moria.org.uk> - 0.6.0
- Use Viktor's spec file as a starting point.

* Fri Jan 20 2006 Viktor Kerkez <alef@atomixlinux.org> - 0.5.0-1.ato
- Initial build for Atomix.

