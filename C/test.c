#include <stdio.h>

int main() {
    int n;
    scanf ("%d", &n);
    int a[9999];
    for (int i = 0; i < n; i++){
        scanf ("%d", &a[i]);
    }
    int so_luong_chan = 0;
    int so_luong_le=0;
    int sum_chan = 0, sum_le = 0;
    for (int i = 0; i < n; i++){
        if (a[i]%2 == 0){
            so_luong_chan++;
            sum_chan += a[i];            
        }
        if (a[i]%2 != 0){
            so_luong_le++;
            sum_le += a[i];
        }
    }
    printf ("%d\n",so_luong_chan);
    printf ("%d\n",so_luong_le);
    printf ("%d\n",sum_chan);
    printf ("%d",sum_le);
    return 0;
}