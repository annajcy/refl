#pragma once

#include <tuple>

#include "refl/demo_models.hpp"

namespace refl {

template <>
struct TypeInfo<demo::Person> {
    static consteval auto members() {
        return std::make_tuple(
            Member{"name", &demo::Person::name},
            Member{"age", &demo::Person::age}
        );
    }
};

template <>
struct TypeInfo<demo::PostalAddress> {
    static consteval auto members() {
        return std::make_tuple(
            Member{"city", &demo::PostalAddress::city},
            Member{"zip_code", &demo::PostalAddress::zip_code}
        );
    }
};

template <>
struct TypeInfo<demo::Employment> {
    static consteval auto members() {
        return std::make_tuple(
            Member{"company", &demo::Employment::company},
            Member{"years", &demo::Employment::years}
        );
    }
};

} // namespace refl
