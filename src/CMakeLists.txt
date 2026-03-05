add_library(refl INTERFACE)
add_library(refl::refl ALIAS refl)

target_compile_features(refl INTERFACE cxx_std_23)
target_include_directories(
    refl
    INTERFACE
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)