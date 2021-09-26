QT       += core gui


greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

SOURCES += main.cpp\
    mainwindow.cpp \
    board.cpp \
    block.cpp

HEADERS  += mainwindow.h \
    board.h \
    block.h\
    gamers.h
    
FORMS += \
    mainwindow.ui