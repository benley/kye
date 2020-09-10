{ nixpkgs ? import <nixpkgs> {} }:

with rec {
  pkgs = nixpkgs.pkgs;
};

pkgs.python27Packages.callPackage ./kye.nix {}
