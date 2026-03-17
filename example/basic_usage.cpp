#include "refl/demo_models.hpp"

#if defined(REFL_USE_GENERATED)
#include "refl/generated.hpp"
#else
#include "refl/demo_manual_typeinfo.hpp"
#endif

int main() {
    demo::Person p{"Alice", 25};

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
