{ nixpkgs ? import <nixpkgs> {} }:

with rec {
  pkgs = nixpkgs.pkgs;

  pythonEnv = pkgs.python38.withPackages (ps: [
    ps.python-language-server
    ps.pyls-mypy
    ps.flake8
  ]);
};

pkgs.mkShell {
  buildInputs = [
    pythonEnv
  ];
  inputsFrom = [
    (import ./default.nix { inherit nixpkgs; })
  ];
}
