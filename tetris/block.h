
#ifndef BLOCK_H
#define BLOCK_H

#include "board.h"
#include <QPainter>

class Board;
class Block
{
public:
    Qt::GlobalColor COLOR[20];//各个类型方块的颜色
	
	Board *board;//地图
    int type;//方块类型
    int nextype;//下一个块编号
    void tonext();//更改方块,方块显示
    void moverotation();//旋转
    void moveright();//加速
    void moveleft();//左移
    void movedown();//右移
    bool detect();//碰撞检测
};
#endif 