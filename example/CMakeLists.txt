add_executable(refl_example basic_usage.cpp)
target_compile_features(refl_example PRIVATE cxx_std_23)
target_link_libraries(refl_example PRIVATE refl::refl)
