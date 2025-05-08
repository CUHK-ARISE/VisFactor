#include<bits/stdc++.h>
using namespace std;
int n = 6; // 定义为全局变量
struct Node
{
    int x,y;
};
struct fig
{
    queue<Node> q;
}mp[10][10];
int valid[10][10]; // 记录哪些点可以打孔，1表示可以，0表示不可以
void fol(Node a, Node b){
    //a 是初始格子 b是目标格子
    //a点对应的map中的queue全部加到b里，a的queue清空
    while(!mp[a.x][a.y].q.empty()){
        Node temp = mp[a.x][a.y].q.front();
        mp[b.x][b.y].q.push(temp);
        mp[a.x][a.y].q.pop();
    }
    // 注意：这里不再设置valid[a.x][a.y] = 0
    // 因为横向和纵向折叠不影响点的有效性
}
int final[10][10];

// 判断点(x,y)是否在折线上或在需要折叠的一侧
bool shouldFold(int x, int y, int mode, int b) {
    // mode 3: 斜率为1的折线 y = x + b
    // mode 4: 斜率为-1的折线 y = -x + b
    if (mode == 3) {
        return (y - x < b); // 在折线下方/左侧的点需要折叠
    } else if (mode == 4) {
        return (y + x < b); // 在折线下方/左侧的点需要折叠
    }
    return false;
}

// 计算点(x,y)关于折线的对称点
Node getSymmetricPoint(int x, int y, int mode, int b) {
    Node result;
    if (mode == 3) { // 斜率为1的折线 y = x + b
        // 计算点到直线的距离
        int dist = (b - (y - x)) / 2;
        // 对称点坐标
        result.x = x + dist;
        result.y = y + dist;
    } else if (mode == 4) { // 斜率为-1的折线 y = -x + b
        // 计算点到直线的距离
        int dist = (b - (y + x)) / 2;
        // 对称点坐标
        result.x = x + dist;
        result.y = y - dist;
    }
    return result;
}

// 判断点是否在折线上
bool isOnFoldLine(int x, int y, int mode, int b) {
    if (mode == 3) {
        return (y - x == b); // 在y = x + b上
    } else if (mode == 4) {
        return (y + x == b); // 在y = -x + b上
    }
    return false;
}

int main(){
    int t;
    cin >> t; // 读取操作次数
    
    // 初始化valid数组，所有位置都有效
    for(int i=1; i<=n; i++) {
        for(int j=1; j<=n; j++) {
            valid[i][j] = 1;
        }
    }
    
    // 初始化mp数组，每个位置包含自己的坐标
    for(int i=1; i<=n; i++){
        for(int j=1; j<=n; j++){
            mp[i][j].q.push({i,j});
        }
    }
    
    // 处理每次折叠操作
    while (t--) {
        int mode, param;
        cin >> mode >> param;
        
        if(mode == 1){ // 水平折叠
            if(param <= 3){ // 下往上
                for(int j=1; j<=param; j++){
                    for(int i=1; i<=n; i++){
                        if(!mp[i][j].q.empty()){ // 只要队列不为空就折叠
                            fol({i,j},{i,2*param-j+1});
                        }
                    }
                }
            }
            else{ // 上往下
                for(int j=6; j>param; j--){
                    for(int i=1; i<=n; i++){
                        if(!mp[i][j].q.empty()){ // 只要队列不为空就折叠
                            fol({i,j},{i,2*param-j+1});
                        }
                    }
                }
            }
        }
        else if(mode == 2){ // 垂直折叠
            if(param <= 3){ // 左往右
                for(int i=1; i<=param; i++){
                    for(int j=1; j<=n; j++){
                        if(!mp[i][j].q.empty()){ // 只要队列不为空就折叠
                            fol({i,j},{2*param-i+1,j});
                        }
                    }
                }
            }   
            else{ // 右往左
                for(int i=6; i>param; i--){
                    for(int j=1; j<=n; j++){
                        if(!mp[i][j].q.empty()){ // 只要队列不为空就折叠
                            fol({i,j},{2*param-i+1,j});
                        }
                    }
                }
            }
        }
        else if(mode == 3 || mode == 4) { // 45°角折叠
            int b; // 截距
            cin >> b;
            
            // 标记折线上的点为无效（不能打孔）
            for(int i=1; i<=n; i++) {
                for(int j=1; j<=n; j++) {
                    if(isOnFoldLine(i, j, mode, b)) {
                        valid[i][j] = 0; // 这里设置valid为0，表示不能打孔
                    }
                }
            }
            
            // 计算哪一侧是小部分（点数较少的一侧）
            int countSmall = 0, countLarge = 0;
            for(int i=1; i<=n; i++) {
                for(int j=1; j<=n; j++) {
                    if(!mp[i][j].q.empty()) {
                        if(shouldFold(i, j, mode, b)) {
                            countSmall++;
                        } else {
                            countLarge++;
                        }
                    }
                }
            }
            
            // 确定折叠方向，小部分向大部分折
            bool foldSmallSide = (countSmall <= countLarge);
            
            // 执行折叠操作
            for(int i=1; i<=n; i++) {
                for(int j=1; j<=n; j++) {
                    if(!mp[i][j].q.empty()) {
                        bool isSmallSide = shouldFold(i, j, mode, b);
                        if((foldSmallSide && isSmallSide) || (!foldSmallSide && !isSmallSide)) {
                            Node symPoint = getSymmetricPoint(i, j, mode, b);
                            // 确保对称点在网格范围内
                            if(symPoint.x >= 1 && symPoint.x <= n && symPoint.y >= 1 && symPoint.y <= n) {
                                fol({i, j}, symPoint);
                            }
                        }
                    }
                }
            }
        }
    }
    
    int tmpx, tmpy;
    cin >> tmpx >> tmpy;
    
    // 检查查询点是否有效（可以打孔）
    if(valid[tmpx][tmpy] == 0) {
        cout << "Cannot punch hole at this position." << endl;
        return 0;
    }
    
    Node tmp = {tmpx, tmpy};
    while(!mp[tmp.x][tmp.y].q.empty()){
        Node p = mp[tmp.x][tmp.y].q.front();
        mp[tmp.x][tmp.y].q.pop();
        final[p.x][p.y] = 1;
    }
    
    // 输出final数组
    for(int i=1; i<=n; i++){
        for(int j=1; j<=n; j++){
            cout << final[i][j] << " ";
        }
        cout << endl;
    }
    return 0;
}
