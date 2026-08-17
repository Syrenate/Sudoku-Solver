#include <sstream>
#include <algorithm>
#include <cmath>
#include <vector>
#include <iostream>
#include <stack>

//#include "BoardComponents.h"
//#include "BoardComponents.cpp"

struct Vector2{
    int row;
    int column;

    Vector2(int r, int c) {
        row = r; column = c;
    }
    Vector2() = default;

    std::string show(){ 
        std::string output;
        std::stringstream ss;

        ss << row;
        ss >> output;

        ss << column;
        ss >> output;

        return output;
    }

    int to_index() {
        // Unique position index on the sudoku board.
        return row + 9 * column;
    }
};

class Tile{
public:
    Vector2 position;
    int value;

    Tile(Vector2 position, int value) {
        this->position = position;
        this->possible_states = 1;
        for (int i = 0; i < 9; i++) {
            this->states[i] = (i+1 == value);
        }
        this->value = value;
    }
    Tile(Vector2 position) {
        this->position = position;
        this->possible_states = 9;
        for (int i = 0; i < 9; i++) {
            this->states[i] = true;
        }
        this->value = 0;
    }
    Tile() = default;

    bool isCollapsed() { return (value > 0); }
    bool collapseState(int state) {
        // Reduce the state space of the tile by a value between 1-9.
        if (states[state-1]) {
            states[state-1] = false;
            possible_states--;

            if (possible_states == 1) {
                for (int i = 0; i < 9; i++) {
                    if (states[i] == true) { value = i+1; }
                }
                return true;
            }
        } 
        return false;
    }

    std::vector<int> get_possible_states() {
        std::vector<int> p_states;
        for (int i=0; i<9; i++) {
            if (states[i]) {
                p_states.push_back(i+1);
            }
        }
        return p_states;
    }

    std::string showStates() {
        std::string output;
        for (int i=0; i<9; i++) {
            output += "(" + std::to_string(i+1) + ": " + std::to_string(states[i]) + ")";
        }
        return output;
    }

private:
    bool states[9];
    int possible_states;
};

class Board{
public:
    Board(std::string config) {
        this->config = config;
        collapsed_tiles = 0;
        state_changed = true;

        int line_index = 0;
        std::string line;
        std::stringstream config_stream(config);

        char empty_chars[3] = {'.', '0', ' '};
        while (std::getline(config_stream, line, ',')) {
            for (int i = 0; i < 9; i++) {
                Vector2 pos(line_index, i);

                char value = line[i];
                bool is_empty = (std::find(std::begin(empty_chars), std::end(empty_chars), value) != std::end(empty_chars));

                if (is_empty) { this->board_state[line_index][i] = Tile(pos); }        
                else          { this->board_state[line_index][i] = Tile(pos, value - '0'); collapsed_tiles++; }
            }
            line_index++;
        }
        _initReferences();
    }
    Board() = default;

    void show() {
        for (int row=0; row<9; row++) {
            for (int col=0; col<9; col++) {
                int value = this->board_state[row][col].value;
                std::cout << ((value == 0) ? "." : std::to_string(value));
            }
            std::cout << "\n";
        }
    }
    bool solve(){
        while (!isSolved() && state_changed) {
            std::cout << this->board_state[0][8].showStates() << std::endl;

            state_changed = false;
            prune();
            show();
        }

        if (isSolved()) { return true; }
        else { return false; }
    }
    bool isSolved(){
        return collapsed_tiles == 81;
    }

    std::vector<Board> branch(){
        auto attempts_start = std::begin(branch_attempts);
        auto attempts_end = std::end(branch_attempts);

        for (int row=0; row<9; row++) {
            for (int col=0; col<9; col++) {
                Tile tile = this->board_state[row][col];
                int index = tile.position.to_index();

                auto search = std::find(attempts_start, attempts_end, index);
                bool new_branch = (search == attempts_end);

                if (!tile.isCollapsed() && new_branch) {
                    std::vector<Board> new_boards = {};
                    for (int state : tile.get_possible_states()) {
                        Board new_board = create_branch(tile.position, state);
                        new_boards.push_back(new_board);
                    }
                    return new_boards;
                }
            }
        }

        return { };
    }


private:
    Tile board_state[9][9];

    std::string config;
    std::vector<int> branch_attempts;

    int collapsed_tiles;
    bool state_changed;

    Tile* rows[9][9];
    Tile* columns[9][9];
    Tile* squares[9][9];

    void _initReferences(){
        for (int row_index = 0; row_index < 9; row_index++) {
            for (int column_index = 0; column_index < 9; column_index++) {
                Tile* tile_ptr = &this->board_state[row_index][column_index];

                int square_index = 3 * floor(row_index / 3) + floor(column_index / 3);
                int square_position = 3 * (row_index % 3) + (column_index % 3);

                rows[row_index][column_index] = tile_ptr;
                columns[column_index][row_index] = tile_ptr;
                squares[square_index][square_position] = tile_ptr;
            }
        }
    }

    void pruneTiles(Tile* tiles[9]){
        std::vector<int> present_values;
        for (int i=0; i < 9; i++) { 
            int value = tiles[i] -> value;
            if (value > 0) {
                present_values.push_back(value);
            } 
        }

        for (int i=0; i<9; i++) {
            if (!tiles[i] -> isCollapsed()) {
                for (int value : present_values) {
                    bool did_collapse = tiles[i] -> collapseState(value);

                    if (did_collapse) {
                        collapsed_tiles++;
                        state_changed = true;
                    }
                }
            }
        }
    }
    void prune() {
        for (int index = 0; index < 9; index++) {
            pruneTiles(rows[index]);
            pruneTiles(columns[index]);
            pruneTiles(squares[index]);
        }
    }

    Board create_branch(Vector2 pos, int state) {
        Board new_board { config };
        new_board.board_state[pos.row][pos.column] = Tile(pos, state);
        return new_board;
    }
};

class Puzzle{
public:
    Puzzle(Board board) {
        board_stack.push(board);
    }
    Puzzle(std::string config) {
        Board board { config };
        board_stack.push(board);
    }

    void show() {
        board_stack.top().show();
    }

    bool solve() {
        Board* board = &board_stack.top();
        //board.show();
        std::cout << std::endl;
        board -> solve();
        //board.show();
        return true;

        while (!board_stack.empty()) {
            Board board = board_stack.top();
            bool got_solved = board.solve();
            board.show();

            if (got_solved) { return true; }
            return false;


            std::vector<Board> branches = board.branch();
            if (branches.empty()) {
                board_stack.pop();
            } else {
                for (Board branch : branches) {
                    board_stack.push(branch);
                }
            }
        }

        return false;
    }

private:
    std::stack<Board> board_stack;
};


int main() {
    Board easy   { "    345  ,  89   3 ,3    2789,2 4  6815,    4    ,8765  4 2,7523    6, 1   79  ,  942    " };
    Board medium { "   4 6 9 ,     3  5,45     86,6 2 74  1,    9    ,9  56 7 8,71     64,3  6     , 6 9 2   " };
    //Board hard   { "9 3  42  ,4 65     ,  28     ,     5  4, 67 4 92 ,1  9     ,     87  ,     94 3,  83  6 1" };
    //Board evil   { "  9      ,384   5  ,    4 3  ,   1  27 ,2  3 4  5, 48  6   ,  6 1    ,  7   629,     5   " };

    
    std::stack<Board> board_stack;
    board_stack.push(easy);
    board_stack.top().show();
    board_stack.top().solve();
    std::cout << std::endl;
    board_stack.top().show();

    return true;


    Puzzle puzzle { easy };
    bool is_solved = puzzle.solve();
    std::cout << std::endl;

    if (is_solved) {
        puzzle.show();
    } else {
        std::cout << "Puzzle is unsolvable!";
    }
    return 0;
}