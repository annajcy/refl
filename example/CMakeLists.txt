add_executable(refl_example basic_usage.cpp)
target_compile_features(refl_example PRIVATE cxx_std_23)
target_link_libraries(refl_example PRIVATE refl::refl)

if(REFL_CODEGEN_ACTIVE)
    add_dependencies(refl_example refl_codegen_header)
    target_compile_definitions(refl_example PRIVATE REFL_USE_GENERATED=1)
    target_include_directories(refl_example PRIVATE "${REFL_CODEGEN_OUTPUT_DIR}")
endif()
