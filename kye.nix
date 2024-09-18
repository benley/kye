{ lib, buildPythonApplication, pygobject3, gtk3
, wrapGAppsHook, gobject-introspection
, pango, pycairo, pyxdg }:

buildPythonApplication rec {
  pname = "Kye";
  version = "1.0";

  src = lib.cleanSource ./.;

  nativeBuildInputs = [
    wrapGAppsHook
    gobject-introspection
  ];

  propagatedBuildInputs = [
    pango
    pygobject3
    gtk3
    pycairo
    pyxdg
  ];
  shellHook = ''
    export MYPYPATH=${pycairo}/${pycairo.pythonModule.sitePackages}/''${MYPYPATH:+:$MYPYPATH}
  '';
}
