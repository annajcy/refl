#pragma once

#include <iostream>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>

namespace refl {

template <typename PtrType>
struct Member {
    std::string_view name;
    PtrType ptr;
};

template <typename T>
struct TypeInfo;

template <typename T>
concept Reflectable = requires {
    { TypeInfo<T>::members() };
};

template <typename T>
    requires Reflectable<std::remove_cvref_t<T>>
consteval auto members() {
    return TypeInfo<std::remove_cvref_t<T>>::members();
}

template<typename T, typename Func>
    requires Reflectable<std::remove_cvref_t<T>>
constexpr void for_each_member(T&& obj, Func&& f) {
    using DecayT = std::remove_cvref_t<T>;
    auto ms = members<DecayT>();

    std::apply([&](const auto&... m) {
        (f(m.name, std::forward<T>(obj).*m.ptr), ...);
    }, ms);
}

} // namespace refl

