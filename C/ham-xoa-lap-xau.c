#include<stdio.h>
#include<string.h>

void removeDuplicates(char s[100]) { //hàm xóa lặp
    int hash[256] = {0}; // Mảng đánh dấu, acsii có 256 phần tử
    int index = 0, i; //index giúp xác định vị trí trong chuỗi khi xóa ký tự trùng, i là biến lặp

    for (i = 0; s[i] != '\0'; i++) {
        if (hash[(unsigned char) s[i]] == 0) { //dùng unsigned char để tránh gặp giá trị âm (không có trong bảng acsii) khiến mảng hash bị lỗi do range từ 0-256
            hash[(unsigned char) s[i]] = 1;
            s[index++] = s[i];
        }
    }
    s[index] = '\0'; //Những ký tự vừa xóa trở thành rỗng, Kết thúc chuỗi
}
int main(){
    char s1[100];
    char s2[100];
    fgets(s1, sizeof(s1), stdin);
    fgets(s2, sizeof(s2), stdin);
    
    removeDuplicates(s1); //đếm ký tự rồi mới xóa lặp
    removeDuplicates(s2);
    printf ("%s", s1);

}