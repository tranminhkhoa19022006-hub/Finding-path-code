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
    fgets(s1, sizeof(s1), stdin); //trống tràn bộ nhớ
    fgets(s2, sizeof(s2), stdin);
    for (int i = 0; i < strlen(s1); i++){ //SẮP XẾP RỒI TÍNH, SAU ĐÓ MỚI XÓA LẶP NHA
        for (int j = i + 1; j < strlen(s1) ; j++){
            if (s1[i] > s1[j]){
                int b = s1[i];
                s1[i] = s1[j];
                s1[j] = b;
            }
        }
    }
    for (int i = 0; i < strlen(s2); i++){
        for (int j = i+1; j < strlen(s2); i++){
            if (s2[i] > s2[j]){
                int b = s2[i];
                s2[i] = s2[j];
                s2[j] = b;
            }
        }
    }
    removeDuplicates(s1);
    removeDuplicates(s2);
}