import React, { Component } from 'react'
import { withRouter } from "react-router-dom";
import qs from "query-string";

class UpsertBoardPage extends Component {
  constructor(props) {
    super(props);

    this.boardId = qs.parse(this.props.location.search)["name"];
    this.state = {
      "loading": this.boardId,
      "name": "",
      "q": "{}",
      "limit": 0,
      "sort": "{}",
      "projections": [],
      "newProjectionName": "",
      "newProjectionJsFilename": "",
      "newProjectionArgs": "[]"
    };

    this.onSubmit = this.onSubmit.bind(this);
    this.onAddProjection = this.onAddProjection.bind(this);
    this.onRemoveProjection = this.onRemoveProjection.bind(this);
    this.onMoveUpProjection = this.onMoveUpProjection.bind(this);
    this.onMoveDownProjection = this.onMoveDownProjection.bind(this)
  }

  componentDidMount() {
    if (this.boardId) {
      this.props.dashboardClient.getBoard(this.boardId)
        .then(data => {
          this.setState({
            "loading": false,
            "name": this.boardId,
            "q": JSON.stringify(data["q"]),
            "limit": data["limit"] ? data["limit"] : 0,
            "sort": data["sort"] ? JSON.stringify(data["sort"]) : "{}",
            "projections": data["projections"].map(p => {
              return {
                "name": p["name"],
                "jsFilename": p["js_filename"],
                "args": JSON.stringify(p["args"])
              }
            })
          })
        })
        .catch(error => {
          this.props.showErrorMessage(`Fail to load board query from board id, error ${error.toString()}`)
        })
    }
  }

  onSubmit(e) {
    this.submit();
    e.preventDefault()
  }

  submit() {
    const {name, q, limit, sort, projections} = this.state;
    this.props.dashboardClient.upsertBoard(
      name,
      JSON.parse(q),
      limit !== 0 ? limit : undefined,
      sort !== "{}" ? JSON.parse(sort) : undefined,
      projections.map(p => {
        return {
          "name": p["name"],
          "js_filename": p["jsFilename"],
          "args": JSON.parse(p["args"])
        }
      }))
        .then(() => {
          this.props.redirectTo("/boards/view");
        })
        .catch(error => {
          this.props.showErrorMessage(`Fail to submit, error ${error.toString()}`)
        })
  }

  onAddProjection(e) {
    this.addProjection();
    e.preventDefault()
  }

  addProjection() {
    this.setState({
      "projections": this.state.projections.concat([{
        "name": this.state.newProjectionName,
        "jsFilename": this.state.newProjectionJsFilename,
        "args": this.state.newProjectionArgs
      }]),
      "newProjectionName": "",
      "newProjectionJsFilename": "",
      "newProjectionArgs": "[]"
    })
  }

  onRemoveProjection(e, name) {
    this.removeProjection(name);
    e.preventDefault()
  }

  removeProjection(name) {
    this.setState({
      ...this.state,
      "projections": this.state.projections.filter(p => {
        return p["name"] !== name
      })
    })
  }

  onMoveUpProjection(e, index) {
    this.moveUpProjection(index);
    e.preventDefault()
  }

  moveUpProjection(index) {
    const projections = this.state.projections;
    [projections[index - 1], projections[index]] = [projections[index], projections[index - 1]];
    this.setState({
      ...this.state,
      "projections": projections
    })
  }

  onMoveDownProjection(e, index) {
    this.moveDownProjection(index);
    e.preventDefault()
  }

  moveDownProjection(index) {
    const projections = this.state.projections;
    [projections[index], projections[index + 1]] = [projections[index + 1], projections[index]];
    this.setState({
      ...this.state,
      "projections": projections
    })
  }

  render() {
    if (this.state.loading) {
      return (<div>Loading...</div>)
    }
    return (
      <div>
        <b>Create new board</b>
        <div>
          Name:<br/>
          <input
            type="text"
            value={this.state.name}
            onChange={e => (this.setState({"name": e.target.value}))}
          /><br/>
          Query:<br/>
          <textarea
            cols="30" rows="5" style={{"resize": "none"}}
            value={this.state.q}
            onChange={e => (this.setState({"q": e.target.value}))}
          /><br/>
          Limit (0 to unset):<br/>
          <input
            type="number"
            value={this.state.limit}
            onChange={e => (this.setState({"limit": parseInt(e.target.value)}))}
          /><br/>
          Sort:<br/>
          <textarea
            cols="30" rows="5" style={{"resize": "none"}}
            value={this.state.sort}
            onChange={e => {this.setState({"sort": e.target.value})}}
          /><br/>
          Projections:<br/>
          <table>
            <thead>
            <tr>
              <th>Name</th>
              <th>Filename</th>
              <th>Args</th>
              <th/>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td>
                <input
                  type="text"
                  value={this.state.newProjectionName}
                  onChange={e => (this.setState({"newProjectionName": e.target.value}))}
                />
              </td>
              <td>
                <input
                  type="text"
                  value={this.state.newProjectionJsFilename}
                  onChange={e => (this.setState({"newProjectionJsFilename": e.target.value}))}
                />
              </td>
              <td>
                <input
                  type="text"
                  value={this.state.newProjectionArgs}
                  onChange={e => (this.setState({"newProjectionArgs": e.target.value}))}
                />
              </td>
              <td>
                <button onClick={e => this.onAddProjection(e)}>+</button>
              </td>
            </tr>
            {this.state.projections.map((projection, index) => {
              const {name, jsFilename, args} = projection;
              return (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{jsFilename}</td>
                  <td>{args}</td>
                  <td>
                    {index !== 0 ? <button onClick={e => {this.onMoveUpProjection(e, index)}}>↑</button> : null}
                    {index !== this.state.projections.length - 1 ? <button onClick={e => {this.onMoveDownProjection(e, index)}}>↓</button> : null}
                    <button onClick={e => this.onRemoveProjection(e, name)}>-</button>
                  </td>
                </tr>
              )
            })}
            </tbody>
          </table>
          <button onClick={this.onSubmit}>Submit</button>
        </div>
      </div>
    )
  }
}

export default withRouter(UpsertBoardPage)
