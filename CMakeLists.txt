cmake_minimum_required(VERSION 3.23)

project(refl VERSION 0.1.0 LANGUAGES CXX)

include(CMakePackageConfigHelpers)
include(CTest)
include(GNUInstallDirs)

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
