#include <sstream>
#include <algorithm>
#include <cmath>
#include <vector>
#include <iostream>
#include "BoardComponents.h"

Board::Board(std::string config) {
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

            if (is_empty) { board_state[line_index][i] = Tile(pos); }        
            else          { board_state[line_index][i] = Tile(pos, value - '0'); collapsed_tiles++; }
        }
        line_index++;
    }
    _initReferences();
}

void Board::show() {
    for (int x = 0; x < 9; x++) {
        for (int y = 0; y < 9; y++) {
            int value = board_state[x][y].value;
            std::cout << ((value == 0) ? "." : std::to_string(value));
        }
        std::cout << "\n";
    }
}

// Pruning Methods

void Board::pruneTiles(Tile* tiles[9]) {
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

void Board::prune() {
    for (int index = 0; index < 9; index++) {
        pruneTiles(rows[index]);
        pruneTiles(columns[index]);
        pruneTiles(squares[index]);
    }
}

bool Board::isFilled() {
    return collapsed_tiles == 81;
}

bool Board::solve() {
    show();
    while (!isFilled() && state_changed) {
        state_changed = false;
        prune();
        show();
        std::cout << std::endl;
    }

    if (isFilled()) { return true; }
    else { return false; }
}

    int collapsed_tiles = 0;
    bool state_changed = true;   // Flag to determine if pruning is necessary (when pruning becomes ineffective.)
    
void Board::_initReferences() {
    for (int row_index = 0; row_index < 9; row_index++) {
        for (int column_index = 0; column_index < 9; column_index++) {
            Tile* tile_ptr = &board_state[row_index][column_index];

            int square_index = 3 * floor(row_index / 3) + floor(column_index / 3);
            int square_position = 3 * (row_index % 3) + (column_index % 3);

            rows[row_index][column_index] = tile_ptr;
            columns[column_index][row_index] = tile_ptr;
            squares[square_index][square_position] = tile_ptr;
        }
    }
}



Vector2::Vector2(int row, int column) {
    this->row = row;
    this->column = column;
}
Vector2::Vector2() = default;

std::string Vector2::show() {
    std::string output;

    std::stringstream ss;
    ss << row;
    ss >> output;

    ss << column;
    ss >> output;

    return output;
}


Tile::Tile(Vector2 position, int value) {
    this->position = position;
    this->possible_states = 1;
    for (int i = 0; i < 9; i++) {
        this->states[i] = (i+1 == value);
    }
    this->value = value;
}

Tile::Tile(Vector2 position) {
    this->position = position;
    this->possible_states = 9;
    for (int i = 0; i < 9; i++) {
        this->states[i] = true;
    }
    this->value = 0;
}
Tile::Tile() = default;

bool Tile::isCollapsed() { return (value > 0); }
bool Tile::collapseState(int state) {
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


