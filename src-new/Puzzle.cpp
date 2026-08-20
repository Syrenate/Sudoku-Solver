#include <sstream>
#include <algorithm>
#include <cmath>
#include <vector>
#include <iostream>
#include <stack>

#include <chrono>
#include <thread>

//#include "BoardComponents.h"
//#include "BoardComponents.cpp"

struct Vector2 {
    int row;
    int column;

    Vector2(int r, int c) {
        row = r; column = c;
    }
    Vector2() { row = -1; column = -1; };

    std::string show(){ 
        std::string output = "(";
        std::stringstream ss;

        ss << row;
        ss >> output;

        output += ", ";

        ss << column;
        ss >> output;

        return output + ")";
    }

    int to_board_index() {
        return row + 9 * column;
    }

    int toSquareIndex() {
        return 3 * floor(row / 3) + floor(column / 3);
    }
};

class Tile {
public:
    Vector2 position;
    int value;

    Tile(Vector2 position, int value) {
        this->position = position;
        this->value = value;

        possible_states = 1;
        for (int i = 0; i < 9; i++) {
            state_space[i] = (i == value);
        }
    }
    Tile(Vector2 position) {
        this->position = position;

        value = -1;
        possible_states = 9;
        for (int i = 0; i < 9; i++) {
            state_space[i] = true;
        }
    }
    Tile() = default;

    bool isCollapsed() { 
        return (possible_states == 1); 
    }

    bool couldBe(int possible_state) {
        return state_space[possible_state];
    }

    bool collapseState(int state) {
        if (!couldBe(state) || isCollapsed()) { return false; }
        
        state_space[state] = false;
        possible_states--;

        if (!isCollapsed()) { return false; } 

        for (int i = 0; i < 9; i++) {
            if (state_space[i]) { 
                value = i; 
                return true;
            }
        }

        return false;
    }

    std::string showStates() {
        std::string output = "(" + std::to_string(position.row) + ", " + std::to_string(position.column) + "): ";
        for (int i=0; i<9; i++) {
            output += "(" + std::to_string(i+1) + ": " + std::to_string(state_space[i]) + ")";
        }
        return output + "\n";
    }

private:
    bool state_space[9];   // The possible states of this tile (state_space[n] == tile might be n+1)
    int possible_states; 
};

class Board {
public:
    Board(std::string config) {
        initial_config = config;
        collapsed_tiles = 0;

        std::string line;
        std::stringstream config_stream(config);
        char empty_chars[3] = {'.', '0', ' '};

        int row_index = 0;
        while (std::getline(config_stream, line, ',')) {
            for (int column_index=0; column_index<9; column_index++) {
                char value = line[column_index];
                bool is_empty = (std::find(std::begin(empty_chars), std::end(empty_chars), value) != std::end(empty_chars));

                Vector2 pos(row_index, column_index);
                Tile tile = is_empty ? Tile(pos) : Tile(pos, (value - '0') - 1);

                board_state[row_index][column_index] = tile;
                if (tile.isCollapsed()) {
                    updateBoard(row_index, column_index, pos.toSquareIndex(), tile.value);
                }
            }
            row_index++;
        }
    }

    void show() {
        for (int row = 0; row < 9; row++) {
            for (int column = 0; column < 9; column++) {
                int value = board_state[row][column].value;
                std::cout << ((value == -1) ? "." : std::to_string(value+1));
            }
            std::cout << "\n";
        }
        std::cout << "\n";
    }

    bool isSolved() {
        return collapsed_tiles == 81;
    }

    bool solve() {
        bool state_changed = true;

        int debug_limit = 2;
        while (!isSolved() && state_changed && debug_limit > 0) {
            state_changed = pruneTiles();
            collapseTiles();
            show();

            debug_limit--;
        }

        if (isSolved()) { return true; }
        else { return false; }
    }

private:
    void updateBoard(int row, int column, int square, int state) {
        //std::cout << "Adding " << std::to_string(state) << " at (" << std::to_string(row);
        //std::cout << ", " << std::to_string(column) << ", " << std::to_string(square) << ")\n";
        //std::cout << "Removing: (" + std::to_string(tile.position.row) + ", " + std::to_string(tile.position.column) + "): " + std::to_string(tile.value) + "\n";
        rows[row][state]       = true;
        columns[column][state] = true;
        squares[square][state] = true;
    }

    bool pruneTiles() {
        bool state_changed = false;

        for (int row_index = 0; row_index < 9; row_index++) {
            for (int column_index = 0; column_index < 9; column_index++) {
                Tile *tile =&board_state[row_index][column_index];
                Vector2 pos = tile->position;

                for (int state = 0; state < 9; state++) {
                    if (rows[row_index][state] || columns[column_index][state] || squares[pos.toSquareIndex()][state]) {
                        //std::cout << std::to_string(state) << ": " << rows[row_index][state] << " " << columns[column_index][state] << " " <<  squares[pos.toSquareIndex()][state] << "\n";
                        bool did_collapse = tile -> collapseState(state);
                        
                        if (row_index == 0 && column_index == 0){ std::cout << std::to_string(column_index) << ": " << state << std::endl; }
                        if (did_collapse) { 
                            state_changed = true; 
                            collapsed_tiles++;
                        }
                    }
                }
            }
        } 

        return state_changed;
    }

    void collapseTiles() {
        for (int row_index = 0; row_index < 9; row_index++) {
            for (int column_index = 0; column_index < 9; column_index++) {
                Tile tile = board_state[row_index][column_index];
                if (tile.isCollapsed()) {
                    updateBoard(row_index, column_index, tile.position.toSquareIndex(), tile.value);
                }
            }
        }
    }

    Tile board_state[9][9];

    // Stores the possible values in each row/column/square (i.e. rows[row_index][n] == row 'row_index' has an 'n' in it)
    bool rows   [9][9];           
    bool columns[9][9];
    bool squares[9][9];

    int collapsed_tiles;
    std::string initial_config;
};



Board solve(Board board) {
    std::stack<Board> board_stack;
    board_stack.push(board);

    while (!board_stack.empty()) {
        Board head_board = board_stack.top();
        bool got_solved = head_board.solve();

        if (got_solved) { return head_board; }

        std::vector<Board> branches = {};//head_board.branch();
        if (branches.empty()) {
            board_stack.pop();
        } else {
            for (Board branch : branches) {
                board_stack.push(branch);
            }
        }
    }

    return board;
}


int main() {
    Board easy   { "    345  ,  89   3 ,3    2789,2 4  6815,    4    ,8765  4 2,7523    6, 1   79  ,  942    " };
    //Board medium { "   4 6 9 ,     3  5,45     86,6 2 74  1,    9    ,9  56 7 8,71     64,3  6     , 6 9 2   " };
    //Board hard   { "9 3  42  ,4 65     ,  28     ,     5  4, 67 4 92 ,1  9     ,     87  ,     94 3,  83  6 1" };
    //Board evil   { "  9      ,384   5  ,    4 3  ,   1  27 ,2  3 4  5, 48  6   ,  6 1    ,  7   629,     5   " };

    easy.show();
    easy.solve();
    return 0;

    //if (solved.isSolved()) {
    //    solved.show();
    //} else {
    //    std::cout << "Puzzle is unsolvable!";
    //}
    //std::cout << "\n\n";


    // THIS does though!
    //easy.solve();
    //easy.show();


    return 0;
}