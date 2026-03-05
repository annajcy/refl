find_package(GTest REQUIRED CONFIG)
include(GoogleTest)

add_executable(refl_smoke_test smoke_test.cpp)
target_compile_features(refl_smoke_test PRIVATE cxx_std_23)
target_link_libraries(refl_smoke_test PRIVATE refl::refl GTest::gtest_main)

gtest_discover_tests(refl_smoke_test)
