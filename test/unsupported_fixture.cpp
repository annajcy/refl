#include "refl/refl.hpp"

class REFL_TYPE PrivateFieldType {
    int hidden;
};

template <typename T>
struct REFL_TYPE TemplateBox {
    T value;
};

struct REFL_TYPE BitfieldType {
    int bits : 3;
};
