#include <tuple>
#include <vector>
#include <string>
#include <string_view>
#include <type_traits>

#include <gtest/gtest.h>

#include "refl/refl.hpp"

namespace {

struct TestPerson {
    std::string name;
    int age;
};

} // namespace

namespace refl {

template <>
struct TypeInfo<TestPerson> {
    static consteval auto members() {
        return std::make_tuple(
            Member{"name", &TestPerson::name},
            Member{"age", &TestPerson::age}
        );
    }
};

} // namespace refl

TEST(SmokeTest, ReflectionReadsAndWrites) {
    TestPerson subject{"Casey", 29};

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
    TestPerson subject{"Jordan", 33};

    refl::for_each_member(subject, [](std::string_view, auto& value) {
        using MemberT = std::remove_cvref_t<decltype(value)>;
        if constexpr (std::is_same_v<MemberT, int>) {
            value += 3;
        }
    });

    EXPECT_EQ(subject.age, 36);
}

TEST(ReflectTest, MembersAcceptsReferences) {
    constexpr auto tuple = refl::members<TestPerson&>();
    constexpr auto count = std::tuple_size_v<decltype(tuple)>;
    EXPECT_EQ(count, 2);
}
