#include<bits/stdc++.h>
using namespace std;
struct Calc
{
    int up,down,left,right,first,second,third,forth;
}Node[100];

int main(){
    freopen("input.txt",'r',stdin);
    memset(Node,0,sizeof(Node));
    for(int i=0;i<8;i++){
        for(int j=0;j<7;j++){
            cin >> Node[i*8+j].up >> Node[i*8+j].down >> Node[i*8+j].left >> Node[i*8+j].right >> Node[i*8+j].first >> Node[i*8+j].second >> Node[i*8+j].third >> Node[i*8+j].forth;
        }
    }
    fclose();
    char tmp1,tmp2;
    cin >> tmp1 >> tmp2;
    
    return 0;
}