const ROWS = 6;
const COLS = 7;
const EMPTY = 0;
const PLAYER = 1;
const AI = 2;

class Connect4 {
    constructor() {
        this.board = Array(ROWS).fill().map(() => Array(COLS).fill(EMPTY));
        this.currentPlayer = PLAYER;
        this.gameOver = false;
        this.setupBoard();
        this.bindEvents();
    }

    setupBoard() {
        const gameBoard = document.getElementById('game-board');
        gameBoard.innerHTML = '';
        
        for (let col = 0; col < COLS; col++) {
            const column = document.createElement('div');
            column.className = 'column';
            column.dataset.col = col;
            
            for (let row = 0; row < ROWS; row++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                column.prepend(cell);
            }
            
            gameBoard.appendChild(column);
        }
    }

    bindEvents() {
        document.getElementById('game-board').addEventListener('click', (e) => {
            if (this.gameOver || this.currentPlayer !== PLAYER) return;
            
            const col = e.target.closest('.column')?.dataset.col;
            if (col !== undefined) {
                this.makeMove(parseInt(col));
            }
        });

        document.getElementById('reset-button').addEventListener('click', () => {
            this.resetGame();
        });
    }

    async updateCell(row, col) {
        const cell = document.querySelector(
            `.cell[data-row="${row}"][data-col="${col}"]`
        );
        cell.className = `cell ${this.currentPlayer === PLAYER ? 'player' : 'ai'} dropping`;
        
        // Wait for animation to complete
        return new Promise(resolve => {
            cell.addEventListener('animationend', () => {
                cell.classList.remove('dropping');
                resolve();
            }, { once: true });
        });
    }

    async makeMove(col) {
        const row = this.getLowestEmptyRow(col);
        if (row === -1) return;

        this.board[row][col] = this.currentPlayer;
        await this.updateCell(row, col);

        const winningCells = this.checkWin(row, col);
        if (winningCells) {
            this.highlightWinningCells(winningCells);
            this.endGame(this.currentPlayer === PLAYER ? 'Player Wins!' : 'AI Wins!');
            return;
        }

        if (this.isBoardFull()) {
            this.endGame("It's a draw!");
            return;
        }

        this.currentPlayer = this.currentPlayer === PLAYER ? AI : PLAYER;
        
        if (this.currentPlayer === AI) {
            setTimeout(() => this.makeAIMove(), 500);
        }
    }

    makeAIMove() {
        const col = this.findBestMove();
        if (col !== -1) {
            this.makeMove(col);
        }
    }

    findBestMove() {
        const validMoves = this.getValidMoves();
        if (validMoves.length === 0) return -1;

        // Simple AI: Prioritize winning moves, then blocking moves, then random
        for (const col of validMoves) {
            const row = this.getLowestEmptyRow(col);
            this.board[row][col] = AI;
            if (this.checkWin(row, col)) {
                this.board[row][col] = EMPTY;
                return col;
            }
            this.board[row][col] = EMPTY;
        }

        for (const col of validMoves) {
            const row = this.getLowestEmptyRow(col);
            this.board[row][col] = PLAYER;
            if (this.checkWin(row, col)) {
                this.board[row][col] = EMPTY;
                return col;
            }
            this.board[row][col] = EMPTY;
        }

        return validMoves[Math.floor(Math.random() * validMoves.length)];
    }

    getValidMoves() {
        return Array.from({length: COLS}, (_, i) => i)
            .filter(col => this.getLowestEmptyRow(col) !== -1);
    }

    getLowestEmptyRow(col) {
        for (let row = ROWS - 1; row >= 0; row--) {
            if (this.board[row][col] === EMPTY) {
                return row;
            }
        }
        return -1;
    }

    checkWin(row, col) {
        const directions = [
            [[0, 1], [0, -1]], // horizontal
            [[1, 0], [-1, 0]], // vertical
            [[1, 1], [-1, -1]], // diagonal /
            [[1, -1], [-1, 1]] // diagonal \
        ];

        const player = this.board[row][col];

        for (const [dir1, dir2] of directions) {
            let count = 1;
            const winningCells = [[row, col]];

            for (const [dx, dy] of [dir1, dir2]) {
                let r = row + dx;
                let c = col + dy;
                
                while (
                    r >= 0 && r < ROWS && 
                    c >= 0 && c < COLS && 
                    this.board[r][c] === player
                ) {
                    count++;
                    winningCells.push([r, c]);
                    r += dx;
                    c += dy;
                }
            }

            if (count >= 4) return winningCells;
        }

        return null;
    }

    highlightWinningCells(cells) {
        for (const [row, col] of cells) {
            const cell = document.querySelector(
                `.cell[data-row="${row}"][data-col="${col}"]`
            );
            cell.classList.add('winner');
        }
    }

    isBoardFull() {
        return this.board.every(row => row.every(cell => cell !== EMPTY));
    }

    endGame(message) {
        this.gameOver = true;
        document.getElementById('status').textContent = message;
    }

    resetGame() {
        this.board = Array(ROWS).fill().map(() => Array(COLS).fill(EMPTY));
        this.currentPlayer = PLAYER;
        this.gameOver = false;
        this.setupBoard();
        document.getElementById('status').textContent = '';
    }
}

// Start the game
new Connect4();

// Add footer to the game
const footer = document.createElement('footer');
footer.innerHTML = `
    <p>This game is made by 
        <a href="https://redwan-rahman.netlify.app/" target="_blank">Redwan Rahman</a>
    </p>`;
document.body.appendChild(footer);
