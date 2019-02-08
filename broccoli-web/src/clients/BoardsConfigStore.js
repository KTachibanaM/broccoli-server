export default class BoardsConfigStore {
  LocalStorageKey = "boardsConfig";

  getBoards() {
    return JSON.parse(window.localStorage.getItem(this.LocalStorageKey) || "[]")
  }

  setBoards(boards) {
    window.localStorage.setItem(this.LocalStorageKey, JSON.stringify(boards));
  }

  getBoardNames() {
    return this.getBoards().map(board => board["name"])
  }

  getBoardIndex(name) {
    return this.getBoardNames().indexOf(name)
  }

  boardExists(name) {
    return this.getBoardIndex(name) !== -1
  }

  getBoard(name) {
    if (!this.boardExists(name)) {
      return false
    }
    return this.getBoards().find(board => board["name"] === name)
  }

  upsertBoard(name, q, columns) {
    if (this.boardExists(name)) {
      const boardIndex = this.getBoardIndex(name);
      const boards = this.getBoards();
      boards[boardIndex] = {name, q, columns};
      this.setBoards(boards)
    } else {
      this.setBoards(this.getBoards().concat([{name, q, columns}]));
    }
  }

  moveBoard(moveIndex, toIndex) {
    const boards = this.getBoards();
    [boards[moveIndex], boards[toIndex]] = [boards[toIndex], boards[moveIndex]];
    this.setBoards(boards)
  }

  removeBoard(index) {
    const boards = this.getBoards();
    boards.splice(index, 1);
    this.setBoards(boards)
  }
}
