import React, { Component } from 'react'
import { Link } from "react-router-dom";

export default class ViewBoardsPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      "boards": [],
      "loading": true
    };
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
                "sort": board["board_query"]["sort"],
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

  render() {
    if (this.state.loading) {
      return (<div>Loading...</div>)
    }
    if (this.state.boards.length === 0) {
      return (<div>No boards</div>)
    }
    return (
      <div>
        <b>View mod views</b>
        <table>
          <thead>
          <tr>
            <th>Name</th>
            <th>Query</th>
            <th>Limit</th>
            <th>Sort</th>
            <th>Columns</th>
          </tr>
          </thead>
          <tbody>
          {this.state.boards.map((board, index) => {
            const {boardId, boardQuery: { q, limit, sort, projections }} = board;
            return (
              <tr key={boardId}>
                <td>
                  <Link to={`/board/${encodeURIComponent(boardId)}`}>{boardId}</Link>
                </td>
                <td>{JSON.stringify(q)}</td>
                <td>{limit ? limit : "N/A"}</td>
                <td>{sort ? JSON.stringify(sort) : "N/A"}</td>
                <td>{projections.map(p => p["name"]).join(", ")}</td>
              </tr>
            )
          })}
          </tbody>
        </table>
      </div>
    );
  }
}
