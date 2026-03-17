from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class ReflConan(ConanFile):
    name = "refl"
    version = "0.1.0"
    package_type = "header-library"

    settings = "os", "compiler", "build_type", "arch"
    options = {"with_tests": [True, False], "with_examples": [True, False]}
    default_options = {"with_tests": False, "with_examples": False}

    exports_sources = (
        "CMakeLists.txt",
        "cmake/*",
        "include/*",
        "src/*",
        "tools/*",
        "example/*",
        "test/*",
    )
    no_copy_source = True

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        if self.options.with_tests:
            self.test_requires("gtest/1.14.0")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 23)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = bool(self.options.with_tests)
        tc.variables["BUILD_EXAMPLES"] = bool(self.options.with_examples)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self.options.with_tests:
            cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "refl")
        self.cpp_info.set_property("cmake_target_name", "refl::refl")
