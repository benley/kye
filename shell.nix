{ nixpkgs ? import <nixpkgs> {} }:

with rec {
  pkgs = nixpkgs.pkgs;

  pythonEnv = pkgs.python38.withPackages (ps: [
    ps.python-language-server
    ps.pyls-mypy
    ps.flake8
    # (ps.callPackage ./kye.nix {})
    ps.pygtk
  ]);
};

pkgs.mkShell {
  buildInputs = [
    pythonEnv
  ];
}
