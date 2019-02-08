import React, { Component } from 'react'
import { Link } from "react-router-dom";

export default class ViewBoardsPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      "boards": this.props.boardsConfigStore.getBoards()
    };

    this.onMoveUp = this.onMoveUp.bind(this);
    this.onMoveDown = this.onMoveDown.bind(this)
  }

  onMoveUp(e, index) {
    this.moveUp(index);
    e.preventDefault()
  }

  moveUp(index) {
    this.props.boardsConfigStore.moveBoard(index, index - 1);
    this.refreshBoards()
  }

  onMoveDown(e ,index) {
    this.moveDown(index);
    e.preventDefault()
  }

  moveDown(index) {
    this.props.boardsConfigStore.moveBoard(index, index + 1);
    this.refreshBoards()
  }

  onRemove(e, index) {
    this.remove(index);
    e.preventDefault()
  }

  remove(index) {
    if (window.confirm(`Are you sure you want to remove board "${this.state.boards[index]["name"]}?"`)){
      this.props.boardsConfigStore.removeBoard(index);
      this.refreshBoards()
    }
  }

  refreshBoards() {
    this.setState({
      "boards": this.props.boardsConfigStore.getBoards()
    })
  }

  render() {
    return (
      <div>
        <b>View boards</b>
        <table>
          <thead>
          <tr>
            <th>Name</th>
            <th>Query</th>
            <th>Operations</th>
          </tr>
          </thead>
          <tbody>
          {this.state.boards.map((board, index) => {
            const {name, q} = board;
            return (
              <tr key={name}>
                <td>
                  <Link to={`/board/${encodeURIComponent(name)}`}>{name}</Link>
                </td>
                <td>
                  {JSON.stringify(q)}
                </td>
                <td>
                  <button
                    onClick={() => this.props.redirectTo(`/boards/upsert?name=${name}`)}
                  >Edit</button>
                  {index !== 0 ? <button onClick={e => {this.onMoveUp(e, index)}}>↑</button> : null}
                  {index !== this.state.boards.length - 1 ? <button onClick={e => {this.onMoveDown(e, index)}}>↓</button> : null}
                  <button onClick={e => {this.onRemove(e, index)}}>x</button>
                </td>
              </tr>
            )
          })}
          </tbody>
        </table>
      </div>
    );
  }
}
