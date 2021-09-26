#ifndef BOARD_H
#define BOARD_H

#include "block.h"

class Block;
class Board
{
public:
    int time;//每次下落的间隔时间
    int width;//地图宽
    int height;//地图高
    
    Block *block;//下落的方块
    char map[100][100];//保存地图信息
    void updatemap();//将下落到底的块更新到游戏地图
    void startGame();//玩家控制游戏开始
    int clearnum();//检测消去行数
    void addto();//碰撞检测后增行
    bool isend();//判断是否游戏结束
    String getWinner();//结算分数得到胜利者名字
    void renewal();//自动循环更新函数：游戏结束后清除本轮游戏数据，释放内存
};

#endif 