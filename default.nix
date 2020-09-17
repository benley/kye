{ nixpkgs ? import <nixpkgs> {} }:

with rec {
  pkgs = nixpkgs.pkgs;
};

pkgs.python38Packages.callPackage ./kye.nix {}
