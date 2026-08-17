#pragma once
#include <sstream>

struct Vector2{
    Vector2(int r, int c);
    Vector2();

    int row;
    int column;

    std::string show();
};

class Tile{
public:
    Vector2 position;
    int value;

    Tile(Vector2 pos, int value);
    Tile(Vector2 pos);
    Tile();

    bool isCollapsed();
    bool collapseState(int state);

private:
    bool states[9];
    int possible_states;
};

class Board{
public:
    Tile board_state[9][9];

    Board(std::string config);
    Board();

    void show();
    bool solve();

private:
    int collapsed_tiles;
    bool state_changed;

    Tile* rows[9][9];
    Tile* columns[9][9];
    Tile* squares[9][9];

    void _initReferences();
    void pruneTiles(Tile* tiles[9]);
    void prune();
    bool isFilled();
};