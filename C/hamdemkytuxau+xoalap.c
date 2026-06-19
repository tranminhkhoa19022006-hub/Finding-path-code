#include <stdio.h>
#include <string.h>

#define MAX_CHAR 256 // Số lượng ký tự ASCII có thể xuất hiện

void countCharacters(const char *s, const char *t, int count[]) {
    // Đếm số lần xuất hiện của từng ký tự trong chuỗi S
    for (int i = 0; s[i] != '\0'; i++) {
        count[(unsigned char)s[i]]++; //dùng unsigned để đỡ bị ra số âm thì sẽ bị tràn gây ra lỗi (range từ 0-256)
    }
    // Đếm số lần xuất hiện của từng ký tự trong chuỗi T
    for (int i = 0; t[i] != '\0'; i++) {
        count[(unsigned char)t[i]]++;
    }
}

void printResults(const int count[]) {
    // In ra các ký tự xuất hiện theo thứ tự ASCII trên cùng một dòng
    for (int i = 0; i < MAX_CHAR; i++) {
        if (count[i] > 0) {
            printf("%c", i);
        }
    }
    printf("\n");

    // In số lần xuất hiện của từng ký tự trên từng dòng riêng biệt
    for (int i = 0; i < MAX_CHAR; i++) {
        if (count[i] > 0) {
            printf("%d\n", count[i]);
        }
    }
}

int main() {
    char S[1000], T[1000];
    int count[MAX_CHAR] = {0}; // Mảng lưu số lần xuất hiện của từng ký tự
    scanf("%s", S);
    scanf("%s", T);

    // Đếm số lần xuất hiện của mỗi ký tự
    countCharacters(S, T, count);

    // Hiển thị kết quả theo định dạng mong muốn
    printResults(count);

    return 0;
}