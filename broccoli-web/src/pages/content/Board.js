import React, { Component } from "react"
import { withRouter } from "react-router-dom";

class Board extends Component {
  constructor(props) {
    super(props);
    this.boardName = decodeURIComponent(this.props.match.params.name);
    this.board = this.props.boardsConfigStore.getBoard(this.boardName);
    this.state = {
      "loading": true,
      "queryPayload": []
    };

    this.reload = this.reload.bind(this)
  }

  componentDidMount() {
    this.reload()
  }

  renderQuery() {
    if (this.state.queryPayload.length === 0) {
      return (<div>No document</div>)
    }
    return (
      <table>
        <thead>
        <tr>
          {this.board.columns.map(({name}) =>
            (<th key={name}>{name}</th>)
          )}
        </tr>
        </thead>
        <tbody>
        {this.state.queryPayload.map(document =>
          (
            <tr key={document["_id"]}>
              {this.board.columns.map(({name, LoadedComponent}) =>
                (<td key={name}>
                  <LoadedComponent
                    document={document}
                    contentClient={this.props.contentClient}
                    reload={this.reload}
                  />
                </td>)
              )}
            </tr>
          )
        )}
        </tbody>
      </table>
    )
  }

  reload() {
    this.setState({
      "loading": true
    });
    Promise.all([
      this.props.contentClient.query(this.board.q),
      ...this.board.columns.map(column => import(`../../columns/${column["fileName"]}`))
    ])
      .then(([queryPayload, ...loadedModules]) => {
        for (let i = 0; i < loadedModules.length; ++i) {
          const loadedModule = loadedModules[i];
          const config = this.board.columns[i];
          this.board.columns[i]["LoadedComponent"] = loadedModule.default(...config["args"])
        }
        this.setState({
          "loading": false,
          "queryPayload": queryPayload
        })
      })
      .catch(error => {
        this.props.showErrorMessage(`Fail to load the query or column components, ${error.toString()}`)
      })
  }

  render() {
    return (
      <div>
        <b>Board "{this.boardName}"</b>
        <button onClick={() => {this.reload()}}>Reload</button>
        <div>Query: {JSON.stringify(this.board.q)}</div>
        {this.state.loading ? <div>Loading the query and column components...</div> : this.renderQuery()}
      </div>
    )
  }
}

export default withRouter(Board)
