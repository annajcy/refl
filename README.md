# refl

Minimal C++23 header-only starter scaffold for a future reflection library.

## Features in this scaffold

- Header-only target: `refl::refl`
- Explicit reflection markers: `REFL_TYPE`, `REFL_IGNORE`
- Clang AST code generator: `tools/refl_codegen/`
- Conan 2 + CMake integration
- GoogleTest smoke test setup (test-only dependency)
- `example/`, `src/`, `test/` project layout
- GitHub Actions CI for macOS/Linux/Windows
- Manual CD workflow running local `conan create`

## Project layout

```
.
├── CMakeLists.txt
├── conanfile.py
├── cmake/
├── tools/
├── src/
├── example/
├── test/
├── test_package/
└── .github/workflows/
```

## Local development

```bash
conan profile detect --force
conan install . --build=missing -s build_type=Release -s compiler.cppstd=23 -o "&:with_tests=True" -o "&:with_examples=True"
cmake --preset conan-release
cmake --build --preset conan-release
ctest --preset conan-release --output-on-failure
```

When the project is configured with a Clang-family compiler, the build also generates `build/<config>/generated/refl/generated.hpp` from Clang AST before compiling the example and tests.

## Clang AST codegen

The v1 generator keeps the runtime API unchanged and only emits `refl::TypeInfo<T>` specializations.

- Mark reflectable types with `REFL_TYPE`: `struct REFL_TYPE Person { ... };`
- Mark fields to skip with `REFL_IGNORE`
- Supported in v1: public non-static data members on non-template `struct`/`class`
- Rejected in v1: inheritance, unignored private/protected fields, templates, anonymous/local types, unions, bit-fields

Manual invocation:

```bash
python3 -m tools.refl_codegen \
  --clang "$(command -v clang++)" \
  --compdb build/Release/compile_commands.json \
  --out-dir build/Release/generated \
  --inputs example/basic_usage.cpp test/smoke_test.cpp
```

The generated header is then available as:

```cpp
#include "refl/generated.hpp"
```

## Create and validate Conan package

```bash
conan create . --build=missing -s build_type=Release -s compiler.cppstd=23
```

`conan create` also runs `test_package` to verify this package can be consumed by another CMake project with:

- `find_package(refl CONFIG REQUIRED)`
- `target_link_libraries(<target> PRIVATE refl::refl)`
