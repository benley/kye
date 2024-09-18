{
  description = "GTK 3 and Python 3 port of the classic Kye puzzle game";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1.tar.gz";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = self.packages.${system}.kye;
        packages.kye = pkgs.python3Packages.callPackage ./kye.nix {};

        devShells.default = pkgs.mkShell {
          buildInputs = [
            (pkgs.python3.withPackages (ps: [
              ps.python-lsp-server
              ps.pylsp-mypy
              ps.pyls-isort
              ps.flake8
            ]))
          ];
          inputsFrom = [self.packages.${system}.kye];
        };
      }
    );
}
