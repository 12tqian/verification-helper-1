---
data:
  attributes:
    '*NOT_SPECIAL_COMMENTS*': ''
  bundledCode: '#line 2 "examples/debug/relative_path.hpp"

    char *hello = "Hello World";

    #line 4 "examples/debug/a/b/c/foo.hpp"

    '
  code: '#pragma once

    #include "../../../relative_path.hpp"

    #include "./.././../../relative_path.hpp"

    '
  dependsOn:
  - examples/debug/relative_path.hpp
  extendedDependsOn:
  - icon: ':warning:'
    path: examples/debug/relative_path.hpp
    title: examples/debug/relative_path.hpp
  extendedRequiredBy:
  - icon: ':heavy_check_mark:'
    path: examples/debug/relative_path.test.cpp
    title: examples/debug/relative_path.test.cpp
  extendedVerifiedWith: []
  isVerificationFile: false
  path: examples/debug/a/b/c/foo.hpp
  requiredBy:
  - examples/debug/relative_path.test.cpp
  timestamp: '2020-03-19 16:25:51+09:00'
  verificationStatus: LIBRARY_NO_TESTS
  verificationStatusIcon: ':warning:'
  verifiedWith: []
documentation_of: examples/debug/a/b/c/foo.hpp
layout: document
redirect_from:
- /library/examples/debug/a/b/c/foo.hpp
- /library/examples/debug/a/b/c/foo.hpp.html
title: examples/debug/a/b/c/foo.hpp
---