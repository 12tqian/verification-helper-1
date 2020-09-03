---
data:
  attributes:
    '*NOT_SPECIAL_COMMENTS*': ''
  bundledCode: "#line 2 \"examples/monoids.hpp\"\n#include <algorithm>\n#include <cstdint>\n\
    \nstruct plus_monoid {\n    typedef int64_t value_type;\n    value_type unit()\
    \ const { return 0; }\n    value_type mult(value_type a, value_type b) const {\
    \ return a + b; }\n};\n\nstruct max_monoid {\n    typedef int64_t value_type;\n\
    \    value_type unit() const { return INT64_MIN; }\n    value_type mult(value_type\
    \ a, value_type b) const { return std::max(a, b); }\n};\n\nstruct min_monoid {\n\
    \    typedef int64_t value_type;\n    value_type unit() const { return INT64_MAX;\
    \ }\n    value_type mult(value_type a, value_type b) const { return std::min(a,\
    \ b); }\n};\n"
  code: "#pragma once\n#include <algorithm>\n#include <cstdint>\n\nstruct plus_monoid\
    \ {\n    typedef int64_t value_type;\n    value_type unit() const { return 0;\
    \ }\n    value_type mult(value_type a, value_type b) const { return a + b; }\n\
    };\n\nstruct max_monoid {\n    typedef int64_t value_type;\n    value_type unit()\
    \ const { return INT64_MIN; }\n    value_type mult(value_type a, value_type b)\
    \ const { return std::max(a, b); }\n};\n\nstruct min_monoid {\n    typedef int64_t\
    \ value_type;\n    value_type unit() const { return INT64_MAX; }\n    value_type\
    \ mult(value_type a, value_type b) const { return std::min(a, b); }\n};\n"
  dependsOn: []
  extendedDependsOn: []
  extendedRequiredBy:
  - icon: ':heavy_check_mark:'
    path: examples/segment_tree.range_minimum_query.test.cpp
    title: examples/segment_tree.range_minimum_query.test.cpp
  - icon: ':heavy_check_mark:'
    path: examples/segment_tree.range_sum_query.test.cpp
    title: examples/segment_tree.range_sum_query.test.cpp
  extendedVerifiedWith: []
  isVerificationFile: false
  path: examples/monoids.hpp
  requiredBy:
  - examples/segment_tree.range_minimum_query.test.cpp
  - examples/segment_tree.range_sum_query.test.cpp
  timestamp: '2019-11-29 11:28:05+09:00'
  verificationStatus: LIBRARY_NO_TESTS
  verificationStatusIcon: ':warning:'
  verifiedWith: []
documentation_of: examples/monoids.hpp
layout: document
redirect_from:
- /library/examples/monoids.hpp
- /library/examples/monoids.hpp.html
title: examples/monoids.hpp
---