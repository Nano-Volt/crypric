#!/usr/bin/env bash
# install-cryptic-syntax.sh
# Installs Cryptic .tmLanguage.json syntax for VS Code, Sublime, and Atom

set -e

CRYPTIC_FILE="cryptic.tmLanguage.json"

# Make sure the grammar file exists
if [ ! -f "$CRYPTIC_FILE" ]; then
    echo "❌ Error: $CRYPTIC_FILE not found. Place it in this folder first."
    exit 1
fi

echo "📦 Installing Cryptic syntax..."

# -------------------------
# VS Code
# -------------------------
VSCODE_DIR="$HOME/.vscode/extensions/cryptic-syntax-0.1.0"
mkdir -p "$VSCODE_DIR/syntaxes"
cp "$CRYPTIC_FILE" "$VSCODE_DIR/syntaxes/cryptic.tmLanguage.json"

# Create package.json for VS Code extension
cat > "$VSCODE_DIR/package.json" <<EOF
{
  "name": "cryptic-syntax",
  "displayName": "Cryptic Syntax",
  "description": "Syntax highlighting for Cryptic language",
  "version": "0.1.0",
  "engines": { "vscode": "^1.0.0" },
  "contributes": {
    "languages": [
      { "id": "cryptic", "aliases": ["Cryptic"], "extensions": [".cryp"] }
    ],
    "grammars": [
      { "language": "cryptic", "scopeName": "source.cryptic", "path": "./syntaxes/cryptic.tmLanguage.json" }
    ]
  }
}
EOF

echo "✅ Installed for VS Code ($VSCODE_DIR)"

# -------------------------
# Sublime Text
# -------------------------
SUBLIME_DIR="$HOME/.config/sublime-text/Packages/User"
mkdir -p "$SUBLIME_DIR"
cp "$CRYPTIC_FILE" "$SUBLIME_DIR/Cryptic.tmLanguage.json"

echo "✅ Installed for Sublime Text ($SUBLIME_DIR)"

# -------------------------
# Atom
# -------------------------
ATOM_DIR="$HOME/.atom/packages/cryptic-syntax"
mkdir -p "$ATOM_DIR/syntaxes"
cp "$CRYPTIC_FILE" "$ATOM_DIR/syntaxes/cryptic.tmLanguage.json"

# Atom package.json
cat > "$ATOM_DIR/package.json" <<EOF
{
  "name": "cryptic-syntax",
  "version": "0.1.0",
  "description": "Cryptic language syntax highlighting",
  "engines": { "atom": ">=1.0.0 <2.0.0" },
  "grammars": [
    {
      "scopeName": "source.cryptic",
      "path": "./syntaxes/cryptic.tmLanguage.json"
    }
  ]
}
EOF

echo "✅ Installed for Atom ($ATOM_DIR)"

echo "🎉 Cryptic syntax installed everywhere! Restart your editors to apply."
