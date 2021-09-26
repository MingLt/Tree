#ifndef GAMERS_H
#define GAMERS_H

#include "block.h"

class Block;
class Board;
class Gamer{
public:
	 Block *block;//下落的方块
	 Board *board;//地图
	 int sumScore();//分数累计函数：统计该玩家总得分
	 String gamerName();//玩家个性化函数：由玩家自定义游戏昵称,附带键盘操作事件
}

#endif 