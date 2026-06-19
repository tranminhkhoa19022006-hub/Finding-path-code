#include <stdio.h>
#include <ctype.h>
#include <string.h>

void trimAndNormalize(char *str) {
    int len = strlen(str);
    int i = 0, j = 0;
    int spaceFlag = 0;

    // Bỏ khoảng trắng ở đầu
    while (str[i] && isspace(str[i])) {
        i++;
    }

    // Chuẩn hóa khoảng trắng giữa các từ
    while (i < len) {
        if (isspace(str[i])) {
            if (!spaceFlag) {
                str[j++] = ' ';
            }
            spaceFlag = 1;
        } else {
            str[j++] = str[i];
            spaceFlag = 0;
        }
        i++;
    }

    // Bỏ khoảng trắng ở cuối
    if (j > 0 && str[j - 1] == ' ') {
        j--;
    }

    str[j] = '\0'; // Kết thúc xâu
}

int main() {
    char title[1000];
    fgets(title, sizeof(title), stdin);

    // Loại bỏ ký tự xuống dòng nếu có
    title[strcspn(title, "\n")] = '\0';

    // Chuẩn hóa tiêu đề
    trimAndNormalize(title);

    // Xuất kết quả
    printf("%s\n", title);

    return 0;
}