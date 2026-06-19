#include<stdio.h>

int main(){
    int a[1000];
    int n;
    scanf ("%d", &n);
    if (n < 0){
        printf ("Error");
    }

    for (int i = 0; i < n; i++){
        scanf ("%d", &a[i]);
    }
    for (int i = 0; i < n; i++){
        for (int j = i + 1; j < n; j++){
            if (a[i]>a[j]){
                int c = a[i];
                a[i] = a[j];
                a[j] = c;
            }
        }
    printf ("%d ", a[i]);
    }
}
