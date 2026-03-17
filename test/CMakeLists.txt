find_package(GTest REQUIRED CONFIG)
include(GoogleTest)

add_executable(refl_smoke_test smoke_test.cpp)
target_compile_features(refl_smoke_test PRIVATE cxx_std_23)
target_link_libraries(refl_smoke_test PRIVATE refl::refl GTest::gtest_main)

add_library(refl_codegen_fixture OBJECT EXCLUDE_FROM_ALL unsupported_fixture.cpp)
target_compile_features(refl_codegen_fixture PRIVATE cxx_std_23)
target_link_libraries(refl_codegen_fixture PRIVATE refl::refl)

if(REFL_CODEGEN_ACTIVE)
    add_dependencies(refl_smoke_test refl_codegen_header)
    target_compile_definitions(refl_smoke_test PRIVATE REFL_USE_GENERATED=1)
    target_include_directories(refl_smoke_test PRIVATE "${REFL_CODEGEN_OUTPUT_DIR}")

    add_test(
        NAME refl_codegen_rejects_unsupported
        COMMAND
            "${CMAKE_COMMAND}"
            -DCOMMAND_TO_RUN=${Python3_EXECUTABLE};-m;tools.refl_codegen;--clang;${CMAKE_CXX_COMPILER};--compdb;${CMAKE_BINARY_DIR}/compile_commands.json;--out-dir;${CMAKE_BINARY_DIR}/negative_codegen;--inputs;${PROJECT_SOURCE_DIR}/test/unsupported_fixture.cpp
            -P "${PROJECT_SOURCE_DIR}/cmake/ExpectFailure.cmake"
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    )
endif()

gtest_discover_tests(refl_smoke_test)
