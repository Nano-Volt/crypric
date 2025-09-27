" Cryptic syntax highlighting for Vim/Neovim
syntax keyword crypticKeyword fn loop print
syntax keyword crypticType int string bool
syntax match crypticNumber "\v[0-9]+"
syntax region crypticString start=/"/ end=/"/
syntax match crypticComment "//.*$"

hi def link crypticKeyword Keyword
hi def link crypticType Type
hi def link crypticNumber Number
hi def link crypticString String
hi def link crypticComment Comment
