#pragma once

#include <string>

#include "refl/refl.hpp"

namespace demo {

struct REFL_TYPE Person {
    std::string name;
    int age;
};

struct REFL_TYPE PostalAddress {
    std::string city;
    int zip_code;
    REFL_IGNORE int internal_code;
};

struct REFL_TYPE Employment {
    std::string company;
    int years;
};

} // namespace demo
