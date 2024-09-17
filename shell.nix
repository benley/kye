{ nixpkgs ? import <nixpkgs> {} }:

with rec {
  pkgs = nixpkgs.pkgs;

  pythonEnv = pkgs.python3.withPackages (ps: [
    ps.python-language-server
    ps.pyls-mypy
    ps.pyls-isort
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
