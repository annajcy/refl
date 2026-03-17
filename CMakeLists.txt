cmake_minimum_required(VERSION 3.23)

project(refl VERSION 0.1.0 LANGUAGES CXX)

include(CMakePackageConfigHelpers)
include(CTest)
include(GNUInstallDirs)

find_package(Python3 COMPONENTS Interpreter)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(REFL_DEFAULT_ENABLE_COMPILE_COMMANDS ${PROJECT_IS_TOP_LEVEL})
option(ENABLE_COMPILE_COMMANDS "Copy compile_commands.json to build root" ${REFL_DEFAULT_ENABLE_COMPILE_COMMANDS})
if (ENABLE_COMPILE_COMMANDS AND PROJECT_IS_TOP_LEVEL)
  set(_SRC "${CMAKE_CURRENT_BINARY_DIR}/compile_commands.json")
  set(_DST "${PROJECT_SOURCE_DIR}/build/compile_commands.json")

  add_custom_target(copy_compile_commands ALL
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${_SRC}" "${_DST}"
    COMMENT "Copying compile_commands.json -> ${_DST}"
    VERBATIM
  )

  message(STATUS "ENABLE_COMPILE_COMMANDS is ON; compile_commands.json will be copied to build root.")
elseif (ENABLE_COMPILE_COMMANDS)
  message(STATUS "ENABLE_COMPILE_COMMANDS is ON; compile_commands copy target is skipped for embedded PBPT builds.")
else()
  message(STATUS "ENABLE_COMPILE_COMMANDS is OFF; compile_commands.json will NOT be copied to build root.")
endif()


option(BUILD_EXAMPLES "Build examples" ON)
set(REFL_DEFAULT_ENABLE_CODEGEN OFF)
if(PROJECT_IS_TOP_LEVEL AND CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  set(REFL_DEFAULT_ENABLE_CODEGEN ON)
endif()
option(REFL_ENABLE_CODEGEN "Generate refl metadata with clang AST during the build" ${REFL_DEFAULT_ENABLE_CODEGEN})

set(REFL_CODEGEN_ACTIVE OFF)
if(REFL_ENABLE_CODEGEN)
  if(NOT Python3_Interpreter_FOUND)
    message(WARNING "REFL_ENABLE_CODEGEN is ON but Python3 was not found; code generation is disabled.")
  elseif(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    message(WARNING "REFL_ENABLE_CODEGEN currently requires a Clang-family compiler; code generation is disabled.")
  else()
    set(REFL_CODEGEN_ACTIVE ON)
    set(REFL_CODEGEN_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
    set(REFL_CODEGEN_HEADER "${REFL_CODEGEN_OUTPUT_DIR}/refl/generated.hpp")
    file(GLOB REFL_CODEGEN_SCRIPT_FILES CONFIGURE_DEPENDS "${PROJECT_SOURCE_DIR}/tools/refl_codegen/*.py")

    set(REFL_CODEGEN_INPUTS)
    if(BUILD_EXAMPLES)
      list(APPEND REFL_CODEGEN_INPUTS "${PROJECT_SOURCE_DIR}/example/basic_usage.cpp")
    endif()
    if(BUILD_TESTING)
      list(APPEND REFL_CODEGEN_INPUTS "${PROJECT_SOURCE_DIR}/test/smoke_test.cpp")
    endif()

    add_custom_command(
      OUTPUT "${REFL_CODEGEN_HEADER}"
      COMMAND "${CMAKE_COMMAND}" -E make_directory "${REFL_CODEGEN_OUTPUT_DIR}/refl"
      COMMAND "${Python3_EXECUTABLE}"
              -m tools.refl_codegen
              --clang "${CMAKE_CXX_COMPILER}"
              --compdb "${CMAKE_CURRENT_BINARY_DIR}/compile_commands.json"
              --out-dir "${REFL_CODEGEN_OUTPUT_DIR}"
              --inputs ${REFL_CODEGEN_INPUTS}
      WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
      DEPENDS
        "${PROJECT_SOURCE_DIR}/tools/__init__.py"
        ${REFL_CODEGEN_SCRIPT_FILES}
        "${PROJECT_SOURCE_DIR}/src/refl/demo_models.hpp"
        ${REFL_CODEGEN_INPUTS}
        "${CMAKE_CURRENT_BINARY_DIR}/compile_commands.json"
      VERBATIM
      COMMENT "Generating refl metadata with clang AST"
    )
    add_custom_target(refl_codegen_header DEPENDS "${REFL_CODEGEN_HEADER}")
  endif()
endif()

add_subdirectory(src)

if(BUILD_EXAMPLES)
    add_subdirectory(example)
endif()

if(BUILD_TESTING)
    add_subdirectory(test)
endif()

install(TARGETS refl EXPORT reflTargets)
install(DIRECTORY ${PROJECT_SOURCE_DIR}/include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

set(refl_cmake_install_dir ${CMAKE_INSTALL_LIBDIR}/cmake/refl)

install(
    EXPORT reflTargets
    FILE reflTargets.cmake
    NAMESPACE refl::
    DESTINATION ${refl_cmake_install_dir}
)

configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/reflConfig.cmake.in
    ${PROJECT_BINARY_DIR}/reflConfig.cmake
    INSTALL_DESTINATION ${refl_cmake_install_dir}
)

write_basic_package_version_file(
    ${PROJECT_BINARY_DIR}/reflConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(
    FILES
        ${PROJECT_BINARY_DIR}/reflConfig.cmake
        ${PROJECT_BINARY_DIR}/reflConfigVersion.cmake
    DESTINATION ${refl_cmake_install_dir}
)
