{ lib, buildPythonApplication, pygtk }:

buildPythonApplication rec {
  pname = "kye";
  version = "1.0";

  src = lib.cleanSource ./.;

  propagatedBuildInputs = [
    pygtk
  ];
}
