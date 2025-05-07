#include<bits/stdc++.h>
using namespace std;
int n = 6; // ← 这里定义为全局变量
struct Node
{
    int x,y;
};
struct fig
{
    queue<Node> q;
}mp[10][10];
int valid[10][10];
void fol(Node a,Node b){
    //a 是初始格子 b是目标格子
    //a点对应的map中的queue全部加到b里，a的queue清空
    //a对应的valid清空
    while(!mp[a.x][a.y].q.empty()){
        Node temp = mp[a.x][a.y].q.front();
        mp[b.x][b.y].q.push(temp);
        mp[a.x][a.y].q.pop();
    }
    valid[a.x][a.y] = 0;
}
int final[10][10];
int main(){
    int t;
    memset(valid,0,sizeof(valid));
    memset(shape,0,sizeof(shape));

    for(int i=1;i<=n;i++){
        for(int j=1;j<=n;j++){
            mp[i][j].q.push({i,j});
        }
    }
    //缺折叠的逻辑
    //每次折的时候新的产生的框的痕迹来自1原先的边缘，2折的那条线 改fol？
    while (t--)
    {
        int mode,x;
        cin >> mode >> x;
        if(mode == 1){
            if(x <= 3){//下往上
                for(int j=1;j<=x;j++){
                    for(int i=1;i<=n;i++){
                        if(valid[i][j]){
                            fol({i,j},{i,2*x-j+1});
                        }
                    }
                }
                for(int j=1;j<=x;j++){
                    for(int i=1;i<=n;i++){
                        valid[i][j] == 0;
                    }
                }
            }
            else{//上往下
                for(int j=6;j>x;j--){
                    for(int i=1;i<=n;i++){
                        if(valid[i][j]){
                            fol({i,j},{i,2*x-j+1});
                        }
                    }
                }
                for(int j=6;j>x;j--){
                    for(int i=1;i<=n;i++){
                        valid[i][j] == 0;
                    }
                }
            }
        }
        else if(mode == 2){
            if(x <= 3){//左往右
                for(int i=1;i<=x;i++){
                    for(int j=1;j<=n;j++){
                        if(valid[i][j]){
                            fol({i,j},{2*x-i+1,j});
                        }
                    }
                }
                for(int i=1;i<=x;i++){
                    for(int j=1;j<=n;j++){
                        valid[i][j] == 0;
                    }
                }
            }   
            else{//右往左
                for(int i=6;i>x;i--){
                    for(int j=1;j<=n;j++){
                        if(valid[i][j]){
                            fol({i,j},{2*x-i+1,j});
                        }
                    }
                }
                for(int i=6;i>x;i--){
                    for(int j=1;j<=n;j++){
                        valid[i][j] == 0;
                    }
                }
            }
        }
    }
    int tmpx,tmpy;
    cin >> tmpx >> tmpy;
    Node tmp = {tmpx,tmpy};
    while(!mp[tmp.x][tmp.y].q.empty()){
        Node p = mp[tmp.x][tmp.y].q.front();
        mp[tmp.x][tmp.y].q.pop();
        final[p.x][p.y] = 1;
    }
    // 输出final数组
    for(int i=1;i<=n;i++){
        for(int j=1;j<=n;j++){
            cout << final[i][j] << " ";
        }
        cout << endl;
    }
    return 0;

}