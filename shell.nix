with { pkgs = import ./nix {}; };
pkgs.mkShell {
  buildInputs = with pkgs; [
    niv
    poetry
    python37Packages.black
    python37Packages.flake8
    python37Packages.pytest
  ];
}
