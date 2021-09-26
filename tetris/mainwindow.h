#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QKeyEvent>
#include "board.h"
#include "gamers.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE


class MainWindow : public QMainWindow

{
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
    void paintboard(Gamer*);//绘制界面
    void keyevent();//键盘事件处理界面

private:
    Ui::MainWindow *ui;

};

#endif 