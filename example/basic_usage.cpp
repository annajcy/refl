#include "refl/refl.hpp"

struct Person {
    std::string name;
    int age;
};

template <>
struct refl::TypeInfo<Person> {
    static consteval auto members() {
        return std::make_tuple(
            refl::Member{ "name", &Person::name },
            refl::Member{ "age", &Person::age }
        );
    }
};


int main() {
    Person p{"Alice", 25};

    // 1. 测试读取：打印所有成员
    std::cout << "--- Read Test ---\n";

    refl::for_each_member(p, [](std::string_view name, const auto& value) {
        std::cout << name << ": " << value << '\n';
    });

    // 2. 测试写入：修改属性
    std::cout << "\n--- Write Test ---\n";
    refl::for_each_member(p, [](std::string_view name, auto& value) {
        if constexpr (std::is_same_v<std::remove_cvref_t<decltype(value)>, int>) {
            value += 1; // 把所有 int 类型的字段加 1
        }
    });

    std::cout << "After modification, age: " << p.age << '\n';
    return 0;
}
