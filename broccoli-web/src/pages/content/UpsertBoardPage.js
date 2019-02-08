import React, { Component } from 'react'
import { withRouter } from "react-router-dom";
import qs from "query-string";

class UpsertBoardPage extends Component {
  constructor(props) {
    super(props);
    let initName= "";
    let initQ = "{}";
    let initColumns = [];

    const query = qs.parse(this.props.location.search);
    if (query["name"]) {
      const {name, q, columns} = this.props.boardsConfigStore.getBoard(query["name"]);
      initName = name;
      initQ = JSON.stringify(q);
      initColumns = columns
    }

    this.state = {
      "name": initName,
      "q": initQ,
      "columns": initColumns,
      "newColumnName": "",
      "newColumnType": "component",
      "newColumnFileName": "",
      "newColumnArgs": "[]"
    };

    this.onSubmit = this.onSubmit.bind(this);
    this.onAddColumn = this.onAddColumn.bind(this);
    this.onRemoveColumn = this.onRemoveColumn.bind(this);
    this.onMoveUpColumn = this.onMoveUpColumn.bind(this);
    this.onMoveDownColumn = this.onMoveDownColumn.bind(this)
  }

  onSubmit(e) {
    this.submit();
    e.preventDefault()
  }

  submit() {
    const {name, q, columns} = this.state;
    this.props.boardsConfigStore.upsertBoard(name, JSON.parse(q), columns);
    this.props.redirectTo("/boards/view");
  }

  onAddColumn(e) {
    this.addColumn();
    e.preventDefault()
  }

  addColumn() {
    this.setState({
      "columns": this.state.columns.concat([{
        "name": this.state.newColumnName,
        "type": this.state.newColumnType,
        "fileName": this.state.newColumnFileName,
        "args": JSON.parse(this.state.newColumnArgs)
      }]),
      "newColumnName": "",
      "newColumnType": "component",
      "newColumnFileName": "",
      "newColumnArgs": "[]"
    })
  }

  onRemoveColumn(e, name) {
    this.removeColumn(name);
    e.preventDefault()
  }

  removeColumn(name) {
    this.setState({
      ...this.state,
      "columns": this.state.columns.filter(column => {
        return column["name"] !== name
      })
    })
  }

  onMoveUpColumn(e, index) {
    this.moveUpColumn(index);
    e.preventDefault()
  }

  moveUpColumn(index) {
    const columns = this.state.columns;
    [columns[index - 1], columns[index]] = [columns[index], columns[index - 1]];
    this.setState({
      ...this.state,
      "columns": columns
    })
  }

  onMoveDownColumn(e, index) {
    this.moveDownColumn(index);
    e.preventDefault()
  }

  moveDownColumn(index) {
    const columns = this.state.columns;
    [columns[index], columns[index + 1]] = [columns[index + 1], columns[index]];
    this.setState({
      ...this.state,
      "columns": columns
    })
  }

  render() {
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
          Columns:<br/>
          <table>
            <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>File name</th>
              {this.state.newColumnType === "factory" ?
                <th>Args</th>
              :
                null
              }
              <th/>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td>
                <input
                  type="text"
                  value={this.state.newColumnName}
                  onChange={e => (this.setState({"newColumnName": e.target.value}))}
                />
              </td>
              <td>
                <select
                  value={this.state.newColumnType}
                  onChange={e => (this.setState({"newColumnType": e.target.value}))}
                >
                  <option value="component">Component</option>
                  <option value="factory">Factory</option>
                </select>
              </td>
              <td>
                <input
                  type="text"
                  value={this.state.newColumnFileName}
                  onChange={e => (this.setState({"newColumnFileName": e.target.value}))}
                />
              </td>
              <td>
                {this.state.newColumnType === "factory" ?
                  <input
                    type="text"
                    value={this.state.newColumnArgs}
                    onChange={e => (this.setState({"newColumnArgs": e.target.value}))}
                  />
                :
                  null
                }
              </td>
              <td>
                <button onClick={e => this.onAddColumn(e)}>+</button>
              </td>
            </tr>
            {this.state.columns.map((column, index) => {
              const {name, type, fileName, args} = column;
              return (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{type}</td>
                  <td>{fileName}</td>
                  <td>{JSON.stringify(args)}</td>
                  <td>
                    {index !== 0 ? <button onClick={e => {this.onMoveUpColumn(e, index)}}>↑</button> : null}
                    {index !== this.state.columns.length - 1 ? <button onClick={e => {this.onMoveDownColumn(e, index)}}>↓</button> : null}
                    <button onClick={e => this.onRemoveColumn(e, name)}>-</button>
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
