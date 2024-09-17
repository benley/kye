{ nixpkgs ? import <nixpkgs> {} }:

with rec {
  pkgs = nixpkgs.pkgs;
};

pkgs.python3Packages.callPackage ./kye.nix {}
