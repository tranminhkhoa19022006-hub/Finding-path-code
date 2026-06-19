#include <stdio.h>

void sortArray(int arr[], int n) {
	for (int i=0; i<n; i++){
        for (int j=i+1; j<n+1; j++){
        if(arr[i]<arr[j]){
            int temp = arr[j];
            arr [j] = arr [i];
            arr [i] = temp;
        }
        }
    }
}

int main() {
    int n;
    int arr[1000];
    scanf ("%d", &n);
    for (int i=0; i<n; i++){
        scanf("%d", &arr[i]);
    }
    sortArray(arr,n);
    for (int i=0; i<n; i++){
        printf("%d ", arr[i]);
    }
}