#include <tuple>
#include <vector>
#include <string>
#include <string_view>
#include <type_traits>

#include <gtest/gtest.h>

#include "refl/demo_models.hpp"

#if defined(REFL_USE_GENERATED)
#include "refl/generated.hpp"
#else
#include "refl/demo_manual_typeinfo.hpp"
#endif

TEST(SmokeTest, ReflectionReadsAndWrites) {
    demo::Person subject{"Casey", 29};

    std::vector<std::string_view> seenNames;
    std::string nameValue;
    int ageSum = 0;

    refl::for_each_member(subject, [&](std::string_view name, auto& value) {
        seenNames.push_back(name);
        using MemberT = std::remove_cvref_t<decltype(value)>;
        if constexpr (std::is_same_v<MemberT, std::string>) {
            nameValue = value;
        } else if constexpr (std::is_same_v<MemberT, int>) {
            ageSum += value;
        }
    });

    EXPECT_EQ(seenNames, (std::vector<std::string_view>{"name", "age"}));
    EXPECT_EQ(nameValue, subject.name);
    EXPECT_EQ(ageSum, subject.age);
}

TEST(ReflectTest, MutatesIntsThroughForEachMember) {
    demo::Person subject{"Jordan", 33};

    refl::for_each_member(subject, [](std::string_view, auto& value) {
        using MemberT = std::remove_cvref_t<decltype(value)>;
        if constexpr (std::is_same_v<MemberT, int>) {
            value += 3;
        }
    });

    EXPECT_EQ(subject.age, 36);
}

TEST(ReflectTest, MembersAcceptsReferences) {
    constexpr auto tuple = refl::members<demo::Person&>();
    constexpr auto count = std::tuple_size_v<decltype(tuple)>;
    EXPECT_EQ(count, 2);
}

TEST(ReflectTest, IgnoresAnnotatedFields) {
    constexpr auto tuple = refl::members<demo::PostalAddress>();
    constexpr auto count = std::tuple_size_v<decltype(tuple)>;
    EXPECT_EQ(count, 2);
}

TEST(ReflectTest, SupportsMultipleNamespacedTypes) {
    demo::Employment subject{"OpenAI", 3};

    std::vector<std::string_view> seenNames;
    refl::for_each_member(subject, [&](std::string_view name, auto&) {
        seenNames.push_back(name);
    });

    EXPECT_EQ(seenNames, (std::vector<std::string_view>{"company", "years"}));
}
