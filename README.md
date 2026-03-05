# refl

Minimal C++23 header-only starter scaffold for a future reflection library.

## Features in this scaffold

- Header-only target: `refl::refl`
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
├── include/refl/refl.hpp
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

## Create and validate Conan package

```bash
conan create . --build=missing -s build_type=Release -s compiler.cppstd=23
```

`conan create` also runs `test_package` to verify this package can be consumed by another CMake project with:

- `find_package(refl CONFIG REQUIRED)`
- `target_link_libraries(<target> PRIVATE refl::refl)`
