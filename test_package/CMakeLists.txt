cmake_minimum_required(VERSION 3.23)
project(test_package LANGUAGES CXX)

find_package(refl CONFIG REQUIRED)

add_executable(test_package src/main.cpp)
target_compile_features(test_package PRIVATE cxx_std_23)
target_link_libraries(test_package PRIVATE refl::refl)
