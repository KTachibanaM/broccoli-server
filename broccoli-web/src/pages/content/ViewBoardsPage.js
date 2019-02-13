import React, { Component } from 'react'
import { Link } from "react-router-dom";

export default class ViewBoardsPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      "boards": [],
      "loading": true
    };

    this.onMoveUp = this.onMoveUp.bind(this);
    this.onMoveDown = this.onMoveDown.bind(this);
  }

  componentDidMount() {
    this.props.apiClient.getBoards()
      .then(boards => {
        this.setState({
          "boards": boards.map(board => {
            return {
              "boardId": board["board_id"],
              "boardQuery": {
                "q": board["board_query"]["q"],
                "limit": board["board_query"]["limit"],
                "projections": board["board_query"]["projections"].map(p => {
                  return {
                    "name": p["name"]
                  }
                }),
              }
            }
          })
        })
      })
      .catch(error => {
        this.props.showErrorMessage(`Fail to get boards, message ${error.toString()}`)
      })
      .finally(() => {
        this.setState({
          "loading": false
        })
      })
  }

  onMoveUp(e, index) {
    this.moveUp(index);
    e.preventDefault()
  }

  moveUp(index) {
    const boardId = this.state.boards[index]["boardId"];
    const anotherBoardId = this.state.boards[index - 1]["boardId"];
    this.props.apiClient.swapBoards(boardId, anotherBoardId)
      .then(() => {
        this.props.showOkMessage(`Moved up board ${boardId}`)
      })
      .catch(error => {
        this.props.showErrorMessage(`Fail to move up board, message ${error.toString()}`)
      })
  }

  onMoveDown(e ,index) {
    this.moveDown(index);
    e.preventDefault()
  }

  moveDown(index) {
    const boardId = this.state.boards[index]["boardId"];
    const anotherBoardId = this.state.boards[index + 1]["boardId"];
    this.props.apiClient.swapBoards(boardId, anotherBoardId)
      .then(() => {
        this.props.showOkMessage(`Moved down board ${boardId}`)
      })
      .catch(error => {
        this.props.showErrorMessage(`Fail to move down board, message ${error.toString()}`)
      })
  }

  onRemove(e, index) {
    this.remove(index);
    e.preventDefault()
  }

  remove(index) {
    const boardId = this.state.boards[index]["boardId"];
    if (window.confirm(`Are you sure you want to remove board "${boardId}?"`)){
      this.props.apiClient.removeBoard(boardId)
        .then(() => {
          this.props.showOkMessage(`Removed board ${boardId}`)
        })
        .catch(error => {
          this.props.showErrorMessage(`Fail to remove board, message ${error.toString()}`)
        })
    }
  }

  render() {
    if (this.state.loading) {
      return (<div>Loading...</div>)
    }
    if (this.state.boards.length === 0) {
      return (<div>No boards</div>)
    }
    return (
      <div>
        <b>View boards</b>
        <table>
          <thead>
          <tr>
            <th>Name</th>
            <th>Query</th>
            <th>Limit</th>
            <th>Projections</th>
            <th>Operations</th>
          </tr>
          </thead>
          <tbody>
          {this.state.boards.map((board, index) => {
            const {boardId, boardQuery: { q, limit, projections }} = board;
            return (
              <tr key={boardId}>
                <td>
                  <Link to={`/board/${encodeURIComponent(boardId)}`}>{boardId}</Link>
                </td>
                <td>{JSON.stringify(q)}</td>
                <td>{limit ? limit : "N/A"}</td>
                <td>{projections.map(p => p["name"]).join(", ")}</td>
                <td>
                  <button
                    onClick={() => this.props.redirectTo(`/boards/upsert?name=${boardId}`)}
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
