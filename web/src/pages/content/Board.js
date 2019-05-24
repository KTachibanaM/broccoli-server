import React, { Component } from "react"
import { withRouter } from "react-router-dom";

class Board extends Component {
  constructor(props) {
    super(props);
    this.boardId = decodeURIComponent(this.props.match.params.name);
    this.state = {
      "loading": true,
      "boardQuery": {},
      "loadedComponents": [],
      "payload": [],
      "countWithoutLimit": 0
    };

    this.reload = this.reload.bind(this)
  }

  componentDidMount() {
    this.props.apiClient.getBoard(this.boardId)
      .then(data => {
        this.setState({
          "boardQuery": {
            "q": data["q"],
            "limit": data["limit"],
            "sort": data["sort"],
            "projections": data["projections"].map(p => {
              return {
                "name": p["name"],
                "jsFilename": p["js_filename"],
                "args": p["args"]
              }
            }),
          },
        });
        return Promise.all(
          this.state.boardQuery.projections.map(p => import('herr-ashi-weblet'))
        )
      })
      .then(loadedModules => {
        console.log(loadedModules)
        const loadedComponents = [];
        for (let i = 0; i < loadedModules.length; ++i) {
          const loadedModule = loadedModules[i];
          const { args } = this.state.boardQuery.projections[i];
          loadedComponents.push(loadedModule.default(...args))
        }
        this.setState({
          "loadedComponents": loadedComponents
        });
        this.reload()
      })
      .catch(error => {
        this.props.showErrorMessage(`Fail to load board or component, error ${error.toString()}`)
      })
      .finally(() => {
        this.setState({
          "loading": false
        })
      })
  }

  renderQuery() {
    return (
      <table>
        <thead>
        <tr>
          {this.state.boardQuery.projections.map(({name}) =>
            (<th key={name}>{name}</th>)
          )}
        </tr>
        </thead>
        <tbody>
        {this.state.payload.map(document =>
          (
            <tr key={document["_id"]}>
              {this.state.boardQuery.projections.map(({name}, index) => {
                const LoadedComponent = this.state.loadedComponents[index];
                return (
                  <td key={name}>
                    <LoadedComponent
                      document={document}
                      apiClient={this.props.apiClient}
                      reload={this.reload}
                    />
                  </td>
                )}
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
    this.props.apiClient.rpcQuery(
      this.state.boardQuery.q,
      this.state.boardQuery.limit,
      this.state.boardQuery.sort
    )
      .then(payload => {
        this.setState({
          "loading": false,
          "payload": payload
        })
      })
      .then(() => {
        return this.props.apiClient.rpcCount(
          this.state.boardQuery.q
        )
      })
      .then(count => {
        this.setState({
          "countWithoutLimit": count
        })
      })
      .catch(error => {
        this.props.showErrorMessage(`Fail to load the query, ${error.toString()}`)
      })
  }

  render() {
    if (this.state.loading) {
      return (<div>Loading components and the query...</div>)
    }
    return (
      <div>
        <b>Board "{this.boardId}"</b>
        <button onClick={() => {this.reload()}}>Reload</button>
        <div>Query: {JSON.stringify(this.state.boardQuery.q)}</div>
        <div>Limit: {this.state.boardQuery.limit ? this.state.boardQuery.limit : 'N/A'}</div>
        <div>Sort: {this.state.boardQuery.sort ? JSON.stringify(this.state.boardQuery.sort) : 'N/A'}</div>
        <div>Count without limit: {this.state.countWithoutLimit}</div>
        {this.renderQuery()}
      </div>
    )
  }
}

export default withRouter(Board)
